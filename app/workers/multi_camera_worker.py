import time
import threading
import queue
import logging
from datetime import datetime
import cv2
import base64
import json
import torch
import collections
from websockets.sync.client import connect

from app.core.database import SessionLocal
from app.models.schema import Camera
from app.cameras.camera_manager import CameraSource
from app.pipeline.detector import PersonDetector
from app.pipeline.tracker import PersonTracker
from app.pipeline.reid import ReIDEncoder
from app.core.kafka import producer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MultiCameraWorker")

INFERENCE_WIDTH = 640

# Shared state for UI Video rendering decoupling
latest_tracks = {} # cam_id -> list of serialized bounding boxes (local_track_id, x1,y1,x2,y2)
latest_tracks_lock = threading.Lock()

class AIWorkerThread(threading.Thread):
    def __init__(self, camera_id: int, frame_queue: queue.Queue):
        super().__init__(daemon=True)
        self.camera_id = camera_id
        self.frame_queue = frame_queue
        self.running = True
        
    def stop(self):
        self.running = False
        
    def run(self):
        logger.info(f"[Cam-{self.camera_id}] Initializing AI Pipeline...")
        
        # Initialize Models
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        logger.info(f"[Cam-{self.camera_id}] Hardware acceleration: {device}")
        
        detector = PersonDetector(model_path="yolov8n.pt")
        tracker = PersonTracker()
        encoder = ReIDEncoder()

        track_embeddings_sent = {}
        
        # Instrumentation metrics
        det_times = collections.deque(maxlen=100)
        track_times = collections.deque(maxlen=100)
        reid_times = collections.deque(maxlen=100)
        kafka_times = collections.deque(maxlen=100)
        frame_counter = 0
        
        while self.running:
            try:
                # Block for up to 1 second waiting for a frame
                frame = self.frame_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            try:
                frame_ts = datetime.utcnow().isoformat()
                
                # --- AI PIPELINE ---
                t_start = time.perf_counter()
                
                h, w = frame.shape[:2]
                scale = INFERENCE_WIDTH / w
                inference_frame = cv2.resize(frame, (INFERENCE_WIDTH, int(h * scale)))
                detections = detector.detect(inference_frame)
                
                if detections:
                    for det in detections:
                        det.bbox = [
                            det.bbox[0] / scale,
                            det.bbox[1] / scale,
                            det.bbox[2] / scale,
                            det.bbox[3] / scale,
                        ]
                        
                t_det = time.perf_counter()
                det_times.append(t_det - t_start)
                
                tracks = tracker.update(detections, frame)
                t_track = time.perf_counter()
                track_times.append(t_track - t_det)
                
                # Extract confirmed tracks for the UI and Kafka
                confirmed_tracks = []
                
                t_reid_start = time.perf_counter()
                for track in tracks:
                    if not track.is_confirmed() or track.time_since_update > 1:
                        continue

                    track_id = track.track_id
                    x1, y1, x2, y2 = map(int, track.to_ltrb())
                    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                    
                    confirmed_tracks.append({
                        "local_track_id": track_id,
                        "bbox": [x1, y1, x2, y2]
                    })

                    # Periodic ReID Embedding Extraction
                    frames_since_last_embed = track_embeddings_sent.get(track_id, 0)
                    if frames_since_last_embed == 0 or frames_since_last_embed >= 30:
                        cx1_crop, cy1_crop = max(0, int(x1 * scale)), max(0, int(y1 * scale))
                        cx2_crop, cy2_crop = min(inference_frame.shape[1], int(x2 * scale)), min(inference_frame.shape[0], int(y2 * scale))
                        if cx2_crop > cx1_crop and cy2_crop > cy1_crop:
                            crop = inference_frame[cy1_crop:cy2_crop, cx1_crop:cx2_crop]
                            embedding = encoder.encode(crop).tolist()
                            
                            t_reid_end = time.perf_counter()
                            reid_times.append(t_reid_end - t_reid_start)
                            
                            t_kafka_start = time.perf_counter()
                            embed_msg = {
                                "camera_id": self.camera_id,
                                "local_track_id": track_id,
                                "embedding": embedding,
                                "x": cx,
                                "y": cy,
                                "frame_ts": frame_ts
                            }
                            producer.produce(topic="reid.embeddings", key=str(self.camera_id), value=embed_msg)
                            t_kafka_end = time.perf_counter()
                            kafka_times.append(t_kafka_end - t_kafka_start)
                            
                            t_reid_start = time.perf_counter() # reset for next track
                            
                        track_embeddings_sent[track_id] = 1
                    else:
                        track_embeddings_sent[track_id] += 1
                        
                    t_kafka_start = time.perf_counter()
                    track_msg = {
                        "camera_id": self.camera_id,
                        "local_track_id": track_id,
                        "x": cx,
                        "y": cy,
                        "frame_ts": frame_ts
                    }
                    producer.produce(topic="camera.tracks", key=str(self.camera_id), value=track_msg)
                    t_kafka_end = time.perf_counter()
                    kafka_times.append(t_kafka_end - t_kafka_start)
                    t_reid_start = time.perf_counter() # reset for next track

                # Update the shared latest_tracks so the main thread can instantly draw them
                with latest_tracks_lock:
                    latest_tracks[self.camera_id] = confirmed_tracks
                    
                frame_counter += 1
                if frame_counter % 100 == 0:
                    avg_det = sum(det_times) / len(det_times) * 1000 if det_times else 0
                    avg_track = sum(track_times) / len(track_times) * 1000 if track_times else 0
                    avg_reid = sum(reid_times) / len(reid_times) * 1000 if reid_times else 0
                    avg_kafka = sum(kafka_times) / len(kafka_times) * 1000 if kafka_times else 0
                    logger.info(f"[Cam-{self.camera_id} PROFILING] Avg Times over 100 frames - Detection: {avg_det:.2f}ms | Tracking: {avg_track:.2f}ms | ReID: {avg_reid:.2f}ms | Kafka: {avg_kafka:.2f}ms")

            except Exception as e:
                logger.error(f"[Cam-{self.camera_id}] Pipeline Error: {e}")
            finally:
                self.frame_queue.task_done()

        logger.info(f"[Cam-{self.camera_id}] AI Worker Stopped.")


# Shared state between DB Poller and Main Thread
desired_cameras = {}
desired_cameras_lock = threading.Lock()

def db_poller_loop():
    """Polls the DB every 5 seconds for camera status changes."""
    while True:
        try:
            db = SessionLocal()
            cameras = db.query(Camera).filter(Camera.status.in_(["starting", "online"])).all()
            
            with desired_cameras_lock:
                desired_cameras.clear()
                for cam in cameras:
                    desired_cameras[cam.id] = {
                        "source_type": cam.source_type,
                        "stream_url": cam.stream_url,
                        "status": cam.status
                    }
                    
                    if cam.status == "starting":
                        cam.status = "online"
                        cam.is_recording = True
                        
                    # Write Health Log
                    from app.models.schema import CameraHealthLog
                    fps = 0.0
                    if cam.id in active_sources_ref:
                        fps = active_sources_ref[cam.id]
                    health_log = CameraHealthLog(
                        camera_id=cam.id,
                        fps=fps,
                        status=cam.status
                    )
                    db.add(health_log)
            
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"DB Poller Error: {e}")
            
        time.sleep(5)


active_sources_ref = {}

def main():
    logger.info("Starting Main-Thread Camera Ingestor...")
    
    # 1. Start the DB Poller Thread
    poller_thread = threading.Thread(target=db_poller_loop, daemon=True)
    poller_thread.start()

    # Active states
    active_sources = {}  # camera_id -> CameraSource
    active_queues = {}   # camera_id -> queue.Queue
    active_workers = {}  # camera_id -> AIWorkerThread
    active_ws = {}       # camera_id -> websocket connection
    
    # Send every 3rd frame to AI (e.g., 10 FPS to AI if webcam is 30 FPS)
    process_every_n_frames = 3 
    
    # Fast UI Publishing settings
    # Publish every frame read to ensure max framerate
    publish_every_n_frames = 1
    
    frame_counts = {}
    
    loop_fps = 30.0
    last_time = time.time()

    try:
        while True:
            # 2. Sync active cameras with desired cameras
            with desired_cameras_lock:
                current_desired = desired_cameras.copy()
                
            desired_ids = set(current_desired.keys())
            active_ids = set(active_sources.keys())
            
            # Stop removed cameras
            for cam_id in active_ids - desired_ids:
                logger.info(f"Stopping Camera {cam_id}")
                active_sources[cam_id].disconnect()
                active_workers[cam_id].stop()
                
                if cam_id in active_ws and active_ws[cam_id]:
                    try:
                        active_ws[cam_id].close()
                    except:
                        pass
                
                with latest_tracks_lock:
                    if cam_id in latest_tracks:
                        del latest_tracks[cam_id]
                
                del active_sources[cam_id]
                del active_workers[cam_id]
                del active_queues[cam_id]
                del frame_counts[cam_id]
                del active_ws[cam_id]
                
            # Start new cameras
            for cam_id in desired_ids - active_ids:
                cam_info = current_desired[cam_id]
                logger.info(f"Connecting to Camera {cam_id} ({cam_info['source_type']})")
                
                source = CameraSource(cam_id, cam_info["source_type"], cam_info["stream_url"])
                if source.connect():
                    active_sources[cam_id] = source
                    
                    # Connect WebSocket publisher
                    ws_url = f"ws://localhost:8000/ws/cameras/{cam_id}/publish"
                    try:
                        active_ws[cam_id] = connect(ws_url)
                    except Exception as e:
                        logger.warning(f"UI WebSocket unreachable for Cam-{cam_id}: {e}")
                        active_ws[cam_id] = None
                        
                    # Queue maxsize=5 prevents memory leaks
                    q = queue.Queue(maxsize=5) 
                    active_queues[cam_id] = q
                    
                    worker = AIWorkerThread(cam_id, q)
                    worker.start()
                    active_workers[cam_id] = worker
                    frame_counts[cam_id] = 0
                else:
                    logger.error(f"Failed to connect to Camera {cam_id}")

            # Update references for poller
            active_sources_ref.clear()
            for c_id, src in active_sources.items():
                active_sources_ref[c_id] = loop_fps # Use loop_fps to represent processing speed

            # 3. Synchronous frame reading loop for ALL active cameras
            for cam_id, source in list(active_sources.items()):
                frame = source.get_frame()
                if frame is not None:
                    frame_counts[cam_id] += 1
                    
                    # -> DISPATCH TO AI PIPELINE
                    if frame_counts[cam_id] % process_every_n_frames == 0:
                        try:
                            # Push frame to AI worker without blocking the main loop
                            active_queues[cam_id].put_nowait(frame.copy())
                        except queue.Full:
                            pass

                    # -> DISPATCH TO FAST UI STREAMING
                    if frame_counts[cam_id] % publish_every_n_frames == 0:
                        ws = active_ws.get(cam_id)
                        if ws:
                            # Get latest tracks computed by the AI worker
                            with latest_tracks_lock:
                                tracks = latest_tracks.get(cam_id, [])
                                
                            display_frame = frame.copy()
                            
                            # Optional: Resize to 640px width to speed up encoding significantly
                            h, w = display_frame.shape[:2]
                            scale = 640.0 / w
                            if scale < 1.0:
                                display_frame = cv2.resize(display_frame, (640, int(h * scale)))
                                # Scale tracks accordingly
                                scaled_tracks = []
                                for track in tracks:
                                    x1, y1, x2, y2 = track['bbox']
                                    scaled_tracks.append({
                                        'local_track_id': track['local_track_id'],
                                        'bbox': [int(x1*scale), int(y1*scale), int(x2*scale), int(y2*scale)]
                                    })
                                tracks = scaled_tracks

                            # Draw bounding boxes
                            for track in tracks:
                                x1, y1, x2, y2 = track['bbox']
                                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                
                            # Dynamic Quality Adjustment
                            # Drop quality if FPS drops, max out at 70, min at 20
                            quality = 60
                            if loop_fps < 15:
                                quality = 30
                            elif loop_fps < 25:
                                quality = 45
                            else:
                                quality = 70
                                
                            _, buffer = cv2.imencode('.jpg', display_frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
                            b64_str = base64.b64encode(buffer).decode('utf-8')
                            
                            frame_ts = datetime.utcnow().isoformat()
                            
                            try:
                                payload = json.dumps({
                                    "camera_id": cam_id,
                                    "frame": f"data:image/jpeg;base64,{b64_str}",
                                    "timestamp": frame_ts,
                                    "persons": tracks
                                })
                                ws.send(payload)
                            except Exception as e:
                                logger.error(f"[Cam-{cam_id}] WS Send Error: {e}")
                                # Try reconnect next cycle?
                                active_ws[cam_id] = None

            curr_time = time.time()
            dt = curr_time - last_time
            last_time = curr_time
            if dt > 0:
                loop_fps = 0.9 * loop_fps + 0.1 * (1.0 / dt)

            if not active_sources:
                time.sleep(0.5)
                loop_fps = 30.0

    except KeyboardInterrupt:
        logger.info("Shutting down Camera Ingestor...")
        for cam_id, source in active_sources.items():
            source.disconnect()
            active_workers[cam_id].stop()
            if cam_id in active_ws and active_ws[cam_id]:
                try:
                    active_ws[cam_id].close()
                except:
                    pass
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    main()
