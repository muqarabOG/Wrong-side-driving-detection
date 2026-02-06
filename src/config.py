import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_VIDEO_DIR = os.path.join(BASE_DIR, "input_videos")
OUTPUT_EVIDENCE_DIR = os.path.join(BASE_DIR, "output_evidence")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Detection Settings
MODEL_PATH = "yolov8n.pt"  # Using nano model for MVP speed
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.5

# Tracking Settings
TRACKER_CONFIDENCE_THRESHOLD = 0.3
TRACKER_IOU_THRESHOLD = 0.5

# Lane Detection Settings
# ROI: (x, y) relative to frame size.
# Defined as a polygon fraction: top-left, top-right, bottom-right, bottom-left
ROI_POINTS = [
    (0.4, 0.6),  # Top-Left
    (0.6, 0.6),  # Top-Right
    (1.0, 0.9),  # Bottom-Right
    (0.0, 0.9)   # Bottom-Left
]

# Violation Settings
MAX_HISTORY_LENGTH = 30  # Frames to keep track history
WRONG_WAY_ANGLE_THRESHOLD = 90.0 # Degrees
VIOLATION_PERSISTENCE = 5 # Frames needed to confirm violation

# Camera settings (can be overridden)
DEFAULT_CAMERA_SOURCE = os.path.join(INPUT_VIDEO_DIR, "sample.mp4")
