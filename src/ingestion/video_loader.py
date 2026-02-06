import cv2
import time
import logging

class VideoLoader:
    def __init__(self, source):
        self.source = source
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            logging.error(f"Failed to open video source: {source}")
            raise ValueError(f"Could not open video source: {source}")
        
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        logging.info(f"Video Source Opened: {source} | Resolution: {self.width}x{self.height} | FPS: {self.fps}")

    def __iter__(self):
        return self

    def __next__(self):
        ret, frame = self.cap.read()
        if not ret:
            raise StopIteration
        return frame

    def release(self):
        self.cap.release()

    def get_info(self):
        return {
            "width": self.width,
            "height": self.height,
            "fps": self.fps
        }
