import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
import numpy as np
from ultralytics import YOLO
import supervision as sv
from config import MODEL_PATH, CONFIDENCE_THRESHOLD

class VehicleDetector:
    def __init__(self, model_path=MODEL_PATH):
        self.model = YOLO(model_path)
        # Class IDs for vehicles in COCO dataset:
        # 2: car, 3: motorcycle, 5: bus, 7: truck
        self.target_classes = [2, 3, 5, 7]
        self.tracker = sv.ByteTrack()
        
    def detect(self, frame):
        """
        Run inference on a frame and return Detections.
        """
        results = self.model(frame, verbose=False, conf=CONFIDENCE_THRESHOLD)[0]
        
        # Convert to supervision Detections
        detections = sv.Detections.from_ultralytics(results)
        
        # Filter by class
        detections = detections[np.isin(detections.class_id, self.target_classes)]
        
        return detections

    def track(self, detections):
        """
        Update tracker and return tracked detections.
        """
        tracked_detections = self.tracker.update_with_detections(detections)
        return tracked_detections
