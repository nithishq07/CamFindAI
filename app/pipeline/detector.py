import cv2
from ultralytics import YOLO

class PersonDetector:
    def __init__(self, model_path="yolov8n.pt", device=None):
        self.model = YOLO(model_path)
        if device:
            self.model.to(device)

    def detect(self, frame):
        """
        Detect persons in the frame.
        Returns:
            list of tuples: ([left, top, width, height], confidence, class_id)
        """
        # Run inference with downscaled resolution for massive speedup
        results = self.model(frame, classes=[0], verbose=False, imgsz=640) # class 0 is 'person' in COCO
        
        detections = []
        for result in results:
            for box in result.boxes:
                # get coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                
                # convert to [left, top, width, height]
                w = x2 - x1
                h = y2 - y1
                detections.append(([x1, y1, w, h], conf, cls_id))
                
        return detections
