import cv2
import supervision as sv
import numpy as np

class Visualizer:
    def __init__(self):
        self.box_annotator = sv.BoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()
        self.trace_annotator = sv.TraceAnnotator()

    def draw_detections(self, frame, detections):
        """
        Draw bounding boxes and labels using supervision.
        detections: sv.Detections
        """
        # Create labels: "ClassID Conf" or "TrackID" if available
        labels = []
        for i in range(len(detections)):
            track_id = detections.tracker_id[i] if detections.tracker_id is not None else "N/A"
            class_id = detections.class_id[i]
            labels.append(f"#{track_id}")

        frame = self.box_annotator.annotate(scene=frame, detections=detections)
        frame = self.label_annotator.annotate(scene=frame, detections=detections, labels=labels)
        frame = self.trace_annotator.annotate(scene=frame, detections=detections)
        return frame

    def draw_lanes(self, frame, lane_mask, src_points):
        """
        Draw the lane overlay.
        """
        # Overlay the mask with transparency
        # lane_mask is single channel, make it BGR (Red for lanes)
        colored_mask = cv2.cvtColor(lane_mask, cv2.COLOR_GRAY2BGR)
        colored_mask[:, :, 0] = 0 # Zero Blue
        colored_mask[:, :, 1] = 0 # Zero Green
        # Red channel is the mask value
        
        frame = cv2.addWeighted(frame, 1, colored_mask, 0.5, 0)
        
        # Draw ROI polygon
        pts = src_points.reshape((-1, 1, 2)).astype(np.int32)
        cv2.polylines(frame, [pts], True, (0, 255, 255), 2)
        
        return frame

    def draw_violations(self, frame, violations):
        """
        Draw big red warnings for violations.
        """
        if not violations:
            return frame
            
        cv2.putText(frame, "WRONG WAY DETECTED!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                    2, (0, 0, 255), 3, cv2.LINE_AA)
        
        for v in violations:
            box = v['box'] # x1, y1, x2, y2
            track_id = v['track_id']
            x1, y1, x2, y2 = map(int, box)
            
            # Draw distinct red box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
            cv2.putText(frame, f"VIOLATION ID: {track_id}", (x1, y1 - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
        return frame
