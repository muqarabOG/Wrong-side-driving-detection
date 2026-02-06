import cv2
import sys
import argparse
from ingestion.video_loader import VideoLoader
from detection.vehicle_detector import VehicleDetector
from lanes.classical_lanes import ClassicalLaneDetector
from violation.logic import ViolationLogic
from ui.visualizer import Visualizer
from config import DEFAULT_CAMERA_SOURCE

def main():
    parser = argparse.ArgumentParser(description="Wrong Side Driving Detection")
    parser.add_argument("--source", type=str, default=None, help="Path to video file or RTSP stream")
    args = parser.parse_args()

    source = args.source if args.source else DEFAULT_CAMERA_SOURCE
    
    # Initialize Core Components
    try:
        loader = VideoLoader(source)
    except Exception as e:
        print(f"Error: {e}")
        print(f"Please provide a valid video path. Usage: python src/main.py --source <path>")
        return

    detector = VehicleDetector()
    lane_detector = ClassicalLaneDetector(loader.width, loader.height)
    logic = ViolationLogic()
    visualizer = Visualizer()
    
    from violation.evidence import EvidenceCollector
    evidence_collector = EvidenceCollector()
    
    print("Starting Main Loop... Press 'q' to quit.")
    
    for frame in loader:
        # Update Evidence Buffer
        evidence_collector.update_buffer(frame)
        
        # 1. Detection & Tracking
        detections = detector.detect(frame)
        tracked_detections = detector.track(detections)
        
        # 2. Lane Detection (Visual only for now in MVP)
        lane_mask = lane_detector.detect_lines(frame) # Just get the lines
        
        # 3. Violation Logic
        # Update tracks and calculate vectors
        movement_data = logic.update_tracks(tracked_detections)
        
        violations = []
        active_violation_ids = set()
        
        for data in movement_data:
            if logic.check_violation(data, loader.width):
                violations.append(data)
                track_id = data['track_id']
                active_violation_ids.add(track_id)
                # Log evidence
                evidence_collector.log_violation_start(track_id, data)
                evidence_collector.log_violation_frame(track_id, frame)
        
        # Check for ended violations (vehicles leaving frame or correcting course)
        # We need to know which IDs were active previously but not now?
        # Simplified: Check evidence_collector's active list
        for tid in list(evidence_collector.active_violations.keys()):
            # If track_id not in current frame detections OR not in current violations list?
            # Let's say if it's no longer violating, we save and close.
            if tid not in active_violation_ids:
                 evidence_collector.log_violation_end(tid)

        # 4. Visualization
        # Draw lanes
        frame = visualizer.draw_lanes(frame, lane_mask, lane_detector.src_points)
        
        # Draw tracks
        frame = visualizer.draw_detections(frame, tracked_detections)
        
        # Draw violations
        frame = visualizer.draw_violations(frame, violations)
        
        # Display
        cv2.imshow("Wrong Side Driving Detection", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup any remaining violations
    for tid in list(evidence_collector.active_violations.keys()):
        evidence_collector.log_violation_end(tid)

    loader.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
