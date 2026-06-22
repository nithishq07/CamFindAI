import cv2

class VideoIngester:
    def __init__(self, source):
        """source can be an RTSP URL or a local video file path"""
        self.source = source
        self.cap = cv2.VideoCapture(self.source)
        
        if not self.cap.isOpened():
            raise ValueError(f"Unable to open video source: {self.source}")
            
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame
        
    def release(self):
        self.cap.release()
