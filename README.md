# Wrong-Side Driving Detection System

A complete full-stack AI system to detect traffic violations from static CCTV feeds.

## System Architecture
-   **Edge Node**: Python + YOLOv8 + ByteTrack. Reads video, detects wrong-way drivers, saves evidence, and syncs with Cloud.
-   **Backend API**: FastAPI. central server for data aggregation and serving evidence.
-   **Dashboard**: React + Tailwind. Real-time monitoring interface for authorities.

## Quick Start

### 1. Prerequisites
-   Python 3.8+
-   Node.js 18+

### 2. Installation
```powershell
# Backend & Detection
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install -r apps/api/requirements.txt

# Frontend
cd apps/web
npm install
```

### 3. Running the System
You need 3 separate terminals.

**Terminal A: Backend API**
```powershell
.\venv\Scripts\activate
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000
```

**Terminal B: Web Dashboard**
```powershell
cd apps/web
npm run dev
```

**Terminal C: Edge Detection Node**
```powershell
.\venv\Scripts\activate
# Run on the static CCTV clip (Best for testing)
python src/main.py --source input_videos/static_violation.mp4
```

## Features
-   [x] Real-time Vehicle Detection (Car, Truck, Bus, Motorcycle)
-   [x] Multi-object Tracking (ID persistence)
-   [x] Wrong-Way Logic (Vector analysis vs Lane direction)
-   [x] Evidence Capture (Video clips + JSON metadata)
-   [x] Web Dashboard (Live alerts)
