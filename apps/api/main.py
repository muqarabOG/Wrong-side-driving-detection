from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import datetime
import os

# App and CORS
app = FastAPI(title="Wrong-Side Driving API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount evidence directory to serve images/videos
# We assume the API runs from project root or we traverse up?
# Let's find the output_evidence path relative to apps/api
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVIDENCE_DIR = os.path.join(BASE_DIR, "output_evidence")

if not os.path.exists(EVIDENCE_DIR):
    os.makedirs(EVIDENCE_DIR)

app.mount("/content", StaticFiles(directory=EVIDENCE_DIR), name="evidence")

# In-memory storage for MVP (Use DB in production)
# We will use this simply to serve the frontend for the demo
violations_db = []

class VehicleData(BaseModel):
    box: List[float]
    vector: List[float]
    centroid: List[float]

class ViolationEvent(BaseModel):
    event_id: str
    timestamp: float
    track_id: int
    vehicle_data: VehicleData
    evidence_path: str
    # metadata fields
    camera_id: Optional[str] = "CAM-01"

@app.post("/violation")
def create_violation(event: ViolationEvent):
    """
    Receive a new violation event from the Edge Node.
    """
    violations_db.append(event.dict())
    print(f"Received Violation: {event.event_id}")
    return {"status": "ok"}

@app.get("/violations")
def get_violations():
    """
    Get all recorded violations.
    """
    # Sort by timestamp desc
    return sorted(violations_db, key=lambda x: x['timestamp'], reverse=True)

@app.get("/stats")
def get_stats():
    """
    Get aggregate stats.
    """
    return {
        "total_violations": len(violations_db),
        "cameras_active": 1
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
