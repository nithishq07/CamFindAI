import cv2
import argparse
import time
from datetime import datetime
from app.pipeline.video_ingest import VideoIngester
from app.pipeline.detector import PersonDetector
from app.pipeline.tracker import PersonTracker
from app.pipeline.reid import ReIDEncoder
from app.core.kafka import producer
from app.core.config import settings
import base64
from websockets.sync.client import connect
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, required=True, help="Path to video file or RTSP stream")
    parser.add_argument("--camera-id", type=int, required=True, help="Camera ID")
    args = parser.parse_args()

    ingester = VideoIngester(args.source)
    detector = PersonDetector(model_path="yolov8n.pt")
    tracker = PersonTracker()
    encoder = ReIDEncoder()

    # Hardware acceleration scaling
    device = settings.DEVICE or encoder.device
    process_every_n_frames = 1
    if device in ['cpu', 'mps']:
        process_every_n_frames = 3 # Drop frames to maintain performance on non-CUDA hardware
        print(f"Warning: Running on {device}. Dropping {process_every_n_frames-1} out of every {process_every_n_frames} frames to maintain throughput.")

    print(f"Starting Camera Worker for Camera ID {args.camera_id} on {args.source}...")
    frame_count = 0
    start_time = time.time()

    # To avoid extracting embeddings every frame for the same track, we keep a counter
    track_embeddings_sent = {}
    
    # Connect to the feed publisher websocket
    ws_url = f"ws://localhost:8000/ws/feeds/{args.camera_id}/publish"
    try:
        ws = connect(ws_url)
        print(f"Connected to live feed publisher at {ws_url}")
    except Exception as e:
        print(f"Warning: Could not connect to feed publisher: {e}")
        ws = None

    while True:
        frame = ingester.read_frame()
        if frame is None:
            break
            
        frame_count += 1
        if frame_count % process_every_n_frames != 0:
            continue

        frame_ts = datetime.utcnow().isoformat()
        
        # 1. Detection
        detections = detector.detect(frame)

        # 2. Tracking
        tracks = tracker.update(detections, frame)

        # 3. Publish to Kafka
        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue

            track_id = track.track_id
            ltrb = track.to_ltrb() # left, top, right, bottom
            x1, y1, x2, y2 = map(int, ltrb)

            # Center coordinates for trajectory
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            # Publish to camera.tracks
            track_msg = {
                "camera_id": args.camera_id,
                "local_track_id": track_id,
                "x": cx,
                "y": cy,
                "frame_ts": frame_ts
            }
            producer.produce(topic="camera.tracks", key=args.camera_id, value=track_msg)

            # ReID Extraction (only send every N frames per track to save bandwidth)
            frames_since_last_embed = track_embeddings_sent.get(track_id, 0)
            if frames_since_last_embed == 0 or frames_since_last_embed >= 30: # every ~1 sec at 30fps
                # Ensure coordinates are within bounds
                cx1, cy1 = max(0, x1), max(0, y1)
                cx2, cy2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                if cx2 > cx1 and cy2 > cy1:
                    crop = frame[cy1:cy2, cx1:cx2]
                    embedding = encoder.encode(crop).tolist() # Convert numpy array to list for JSON serialization
                    
                    embed_msg = {
                        "camera_id": args.camera_id,
                        "local_track_id": track_id,
                        "embedding": embedding,
                        "x": cx,
                        "y": cy,
                        "frame_ts": frame_ts
                    }
                    producer.produce(topic="reid.embeddings", key=args.camera_id, value=embed_msg)
                track_embeddings_sent[track_id] = 1
            else:
                track_embeddings_sent[track_id] += 1

        if ws:
            # Draw tracks on the frame for live view
            display_frame = frame.copy()
            for track in tracks:
                if not track.is_confirmed() or track.time_since_update > 1:
                    continue
                x1, y1, x2, y2 = map(int, track.to_ltrb())
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(display_frame, f"ID: {track.track_id}", (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Compress and encode to base64
            _, buffer = cv2.imencode('.jpg', display_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
            b64_str = base64.b64encode(buffer).decode('utf-8')
            
            try:
                # Send frame and metadata
                payload = json.dumps({
                    "frame": f"data:image/jpeg;base64,{b64_str}",
                    "timestamp": frame_ts,
                    "active_tracks": len([t for t in tracks if t.is_confirmed() and t.time_since_update <= 1])
                })
                ws.send(payload)
            except Exception as e:
                print(f"WebSocket error: {e}")
                ws = None # Drop connection if it fails

        if frame_count % (30 * process_every_n_frames) == 0:
            elapsed = time.time() - start_time
            fps = frame_count / elapsed
            print(f"Read {frame_count} frames (Processed {frame_count // process_every_n_frames}), Input FPS: {fps:.2f}")

    producer.flush()
    if ws:
        ws.close()
    ingester.release()
    print(f"Finished processing camera {args.camera_id}.")

if __name__ == "__main__":
    main()
