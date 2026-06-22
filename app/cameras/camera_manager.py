import cv2
import time
import logging
import threading
import queue

logger = logging.getLogger(__name__)

class CameraSource:
    def __init__(self, camera_id: int, source_type: str, stream_url: str):
        self.camera_id = camera_id
        self.source_type = source_type
        
        # Determine source correctly
        if self.source_type == "WEBCAM":
            try:
                self.stream_url = int(stream_url)
            except ValueError:
                logger.warning(f"Invalid webcam source: {stream_url}, defaulting to 0")
                self.stream_url = 0
        else:
            self.stream_url = stream_url
            
        self.cap = None
        self._is_connected = False
        
        self.frame_queue = queue.Queue(maxsize=1)
        self.read_thread = None

    def connect(self):
        logger.info(f"Connecting to Camera {self.camera_id} [{self.source_type}] -> {self.stream_url}")
        self.cap = cv2.VideoCapture(self.stream_url)
        
        # Adjust buffer size for IP/RTSP to reduce latency
        if self.source_type in ["IP_CAMERA", "RTSP"]:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():
            logger.error(f"Failed to open Camera {self.camera_id}")
            self._is_connected = False
            return False
            
        self._is_connected = True
        
        # Start background reading thread
        self.read_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.read_thread.start()
        
        return True

    def _update_loop(self):
        while self._is_connected:
            if not self.cap:
                break
                
            ret, frame = self.cap.read()
            if ret:
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                self.frame_queue.put(frame)
            else:
                logger.warning(f"Frame read failed for Camera {self.camera_id}")
                time.sleep(0.1) # Prevent tight spin on error

    def disconnect(self):
        self._is_connected = False
        if self.read_thread:
            self.read_thread.join(timeout=1.0)
            
        if self.cap:
            self.cap.release()
            logger.info(f"Disconnected Camera {self.camera_id}")

    def get_frame(self):
        if not self._is_connected:
            return None
            
        try:
            return self.frame_queue.get(timeout=1.0)
        except queue.Empty:
            return None

    def is_online(self):
        return self._is_connected and self.cap and self.cap.isOpened()

    def get_fps(self):
        if self.is_online():
            return self.cap.get(cv2.CAP_PROP_FPS)
        return 0.0
