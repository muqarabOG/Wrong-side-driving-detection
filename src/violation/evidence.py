import cv2
import json
import os
import time
import uuid
import requests
import numpy as np
from collections import deque
from config import OUTPUT_EVIDENCE_DIR

# API Configuration
API_URL = "http://localhost:8000/violation"

class EvidenceCollector:
    def __init__(self, buffer_size=300): # 300 frames @ 30fps = 10 seconds history
        self.buffer_size = buffer_size
        self.frame_buffer = deque(maxlen=buffer_size)
        self.active_violations = {} # track_id -> {start_time, frames}
        
        if not os.path.exists(OUTPUT_EVIDENCE_DIR):
            os.makedirs(OUTPUT_EVIDENCE_DIR)

    def update_buffer(self, frame):
        """
        Add current frame to the circular buffer.
        """
        self.frame_buffer.append(frame.copy())

    def log_violation_start(self, track_id, vehicle_data):
        """
        Called when a violation logic confirms a NEW violation.
        """
        if track_id not in self.active_violations:
            self.active_violations[track_id] = {
                "id": str(uuid.uuid4()),
                "track_id": track_id,
                "start_time": time.time(),
                "data": vehicle_data,
                "violation_frames": []
            }
            print(f"[EvidenceCollector] Violation Started: {track_id}")

    def log_violation_frame(self, track_id, frame):
        """
        Accumulate frames during the violation event.
        """
        if track_id in self.active_violations:
            self.active_violations[track_id]["violation_frames"].append(frame.copy())

    def log_violation_end(self, track_id):
        """
        Called when violation ends (or vehicle leaves). Triggers save.
        """
        if track_id in self.active_violations:
            self.save_evidence(track_id)
            del self.active_violations[track_id]

    def save_evidence(self, track_id):
        """
        Compile the clip (History + Event) and save to disk.
        """
        violation = self.active_violations[track_id]
        event_id = violation["id"]
        
        # 1. Prepare Video Frames
        # Combine historical buffer + violation frames
        all_frames = list(self.frame_buffer) + violation["violation_frames"]
        
        if not all_frames:
            return

        h, w, _ = all_frames[0].shape
        
        # Paths
        video_path = os.path.join(OUTPUT_EVIDENCE_DIR, f"violation_{event_id}.mp4")
        json_path = os.path.join(OUTPUT_EVIDENCE_DIR, f"violation_{event_id}.json")
        img_path = os.path.join(OUTPUT_EVIDENCE_DIR, f"violation_{event_id}.jpg")
        
        # 2. Save Video
        out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (w, h))
        for f in all_frames:
            out.write(f)
        out.release()
        
        # 3. Save Snapshot (First frame of violation)
        if violation["violation_frames"]:
            cv2.imwrite(img_path, violation["violation_frames"][0])
        elif all_frames:
            cv2.imwrite(img_path, all_frames[-1])

        # 4. Save Metadata
        def sanitize(obj):
            if isinstance(obj, (np.integer, np.int32, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize(v) for v in obj]
            return obj

        meta = {
            "event_id": event_id,
            "timestamp": violation["start_time"],
            "track_id": int(violation["track_id"]), # Explicit cast
            "vehicle_data": {
                "box": [float(x) for x in violation["data"]["box"]], 
                "vector": [float(x) for x in violation["data"]["vector"]],
                "centroid": [float(x) for x in violation["data"]["centroid"]]
            },
            "evidence_path": video_path
        }
        
        # Sanitize everything just in case
        meta = sanitize(meta)
        
        with open(json_path, 'w') as f:
            json.dump(meta, f, indent=4)
            
        print(f"[EvidenceCollector] Evidence Saved: {video_path}")
        
        # 5. Send to API (Fire and Forget)
        try:
            # We need to make sure data types are JSON serializable (already done in meta)
            # Add camera_id
            meta["camera_id"] = "CAM-01"
            
            # The API expects specific schema. 
            # Our meta keys match ViolationEvent model:
            # - event_id, timestamp, track_id, vehicle_data, evidence_path
            
            # We might want to serve the evidence file via a static server or upload it.
            # For MVP, we send the absolute path (works since API is on same machine)
            
            response = requests.post(API_URL, json=meta)
            if response.status_code == 200:
                print(f"[EvidenceCollector] Synced with API.")
            else:
                print(f"[EvidenceCollector] API Error: {response.text}")
        except Exception as e:
            print(f"[EvidenceCollector] Failed to sync with API: {e}")
