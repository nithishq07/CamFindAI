import cv2
import argparse
import time
from app.pipeline.video_ingest import VideoIngester
from app.pipeline.detector import PersonDetector
from app.pipeline.tracker import PersonTracker

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, required=True, help="Path to video file or RTSP stream")
    parser.add_argument("--output", type=str, default="output.mp4", help="Path to output video file")
    args = parser.parse_args()

    ingester = VideoIngester(args.source)
    detector = PersonDetector(model_path="yolov8n.pt")
    tracker = PersonTracker()

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.output, fourcc, ingester.fps, (ingester.width, ingester.height))

    print(f"Starting pipeline on {args.source}...")
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

        # 3. Draw Bounding Boxes
        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue

            track_id = track.track_id
            ltrb = track.to_ltrb() # left, top, right, bottom
            x1, y1, x2, y2 = map(int, ltrb)

            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # Draw label
            label = f"ID-{track_id}"
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
