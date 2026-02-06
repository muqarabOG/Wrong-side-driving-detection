import requests
import uuid
import time
import os

API_URL = "http://localhost:8000/violation"

def seed():
    event_id = str(uuid.uuid4())
    payload = {
        "event_id": event_id,
        "timestamp": time.time(),
        "track_id": 999,
        "vehicle_data": {
            "box": [100.0, 100.0, 200.0, 200.0],
            "vector": [0.0, -10.0],
            "centroid": [150.0, 150.0]
        },
        "evidence_path": r"C:\fake\path\to\violation_test.mp4",
        "camera_id": "TEST-CAM"
    }
    
    try:
        res = requests.post(API_URL, json=payload)
        if res.status_code == 200:
            print("Successfully seeded test violation!")
        else:
            print(f"Failed to seed: {res.status_code} {res.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    seed()
