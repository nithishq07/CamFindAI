import cv2
import argparse
import time
from app.pipeline.video_ingest import VideoIngester
from app.pipeline.detector import PersonDetector
from app.pipeline.tracker import PersonTracker
from app.pipeline.reid import ReIDEncoder
from app.pipeline.matcher import IdentityMatcher

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, required=True, help="Path to video file or RTSP stream")
    parser.add_argument("--output", type=str, default="output_phase2.mp4", help="Path to output video file")
    args = parser.parse_args()

    ingester = VideoIngester(args.source)
    detector = PersonDetector(model_path="yolov8n.pt")
    tracker = PersonTracker()
    encoder = ReIDEncoder()
    matcher = IdentityMatcher(embedding_dim=encoder.embedding_dim)

    # Dictionary to keep track of local_track_id to global_id mapping
    track_to_global = {}

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.output, fourcc, ingester.fps, (ingester.width, ingester.height))

    print(f"Starting Phase 2 pipeline on {args.source}...")
    frame_count = 0
    start_time = time.time()

    while True:
        frame = ingester.read_frame()
        if frame is None:
            break

        # 1. Detection
        detections = detector.detect(frame)

        # 2. Tracking
        tracks = tracker.update(detections, frame)

        # 3. ReID & Matching
        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue

            track_id = track.track_id
            ltrb = track.to_ltrb() # left, top, right, bottom
            x1, y1, x2, y2 = map(int, ltrb)

            # Ensure coordinates are within frame bounds
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

            if x2 <= x1 or y2 <= y1:
                continue

            # If we don't have a global_id for this track yet, run ReID
            if track_id not in track_to_global:
                # Extract crop
                crop = frame[y1:y2, x1:x2]
                # Encode
                embedding = encoder.encode(crop)
                # Match
                global_id = matcher.match(embedding)
                track_to_global[track_id] = global_id

            global_id = track_to_global[track_id]

            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # Draw label
            label = f"{global_id}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Write output frame
        out.write(frame)
        
        frame_count += 1
        if frame_count % 30 == 0:
            elapsed = time.time() - start_time
            fps = frame_count / elapsed
            print(f"Processed {frame_count} frames, FPS: {fps:.2f}")

    ingester.release()
    out.release()
    print(f"Finished processing. Output saved to {args.output}")

if __name__ == "__main__":
    main()
