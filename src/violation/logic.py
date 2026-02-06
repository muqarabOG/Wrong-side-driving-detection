import numpy as np
import collections

class ViolationLogic:
    def __init__(self):
        # Map track_id -> deque of recent positions (centroids)
        self.track_history = collections.defaultdict(lambda: collections.deque(maxlen=30))
        self.confirmed_violations = set() # Set of track_ids currently violating

    def update_tracks(self, detections):
        """
        detections: supervision Detections object with tracker_id
        """
        if detections.tracker_id is None:
            return []

        violations = []
        
        for xyxy, track_id in zip(detections.xyxy, detections.tracker_id):
            x1, y1, x2, y2 = xyxy
            centroid = ((x1 + x2) / 2, (y1 + y2) / 2)
            
            self.track_history[track_id].append(centroid)
            
            if len(self.track_history[track_id]) >= 5:
                # Calculate vector
                start_point = self.track_history[track_id][0]
                end_point = self.track_history[track_id][-1]
                
                dx = end_point[0] - start_point[0]
                dy = end_point[1] - start_point[1]
                
                # Check violation
                # MVP Rule: If on the LEFT side of the screen, should be checking if moving DOWN (dy > 0)
                # If on the RIGHT side, should be moving UP (dy < 0)
                # Ideally this depends on 'Lanes' but let's hardcode a divider for MVP at x = width/2
                
                # We need frame width for this simple logic. 
                # Let's assume passed in or configured or we check relative to something.
                # For now, let's just return the vector info for the main loop to decide.
                
                violations.append({
                    "track_id": track_id,
                    "box": xyxy,
                    "vector": (dx, dy),
                    "centroid": centroid
                })
        
        return violations
        
    def check_violation(self, vehicle_data, frame_width):
        """
        Enhanced Logic: 
        1. Check geometry (Left vs Right lane).
        2. Require persistence (VIOLATION_PERSISTENCE frames).
        """
        from config import VIOLATION_PERSISTENCE
        
        vid_w = frame_width
        centroid_x = vehicle_data["centroid"][0]
        dx, dy = vehicle_data["vector"]
        track_id = vehicle_data["track_id"]
        
        # DEBUG: Print vector to see what's happening
        # print(f"ID {track_id}: Centroid={centroid_x:.1f}, Vector=({dx:.2f}, {dy:.2f})")
        
        is_violation_instant = False
        
        # Simple Logic: Divider at 50% width
        if centroid_x < vid_w / 2:
            # LEFT LANE -> Expected DOWN (dy > 0). Violation if Moving UP (dy < -5)
            # NOTE: In computer vision (0,0) is Top-Left. 
            # Down = y increases (dy > 0). Up = y decreases (dy < 0).
            # If camera is looking AT oncoming traffic:
            # They move Down (dy > 0). 
            # Wrong way would be moving UP (dy < 0) - i.e. away from camera? 
            # It depends on the camera angle.
            
            # Let's log potential issues
            if dy < -5: 
                print(f"[DEBUG] Potential Violation Left: ID {track_id} dy={dy:.2f}")
                is_violation_instant = True
        else:
            # RIGHT LANE -> Expected UP (dy < 0). Violation if Moving DOWN (dy > 5)
            if dy > 5:
                print(f"[DEBUG] Potential Violation Right: ID {track_id} dy={dy:.2f}")
                is_violation_instant = True
                
        # Persistence Check
        if is_violation_instant:
            # Increment potential violation counter?
            # Or simplified: We check if this track_id has been 'bad' for N frames.
            # We can use the history we already have.
            
            # Let's count how many recent frames were "wrong way"
            # Optimization: Just return True if we have > N consecutive bad movements
            pass # Logic happens in main loop or we store state here?
            
            # Let's verify using the history vector logic we already computed for the *current* frame.
            # Ideally we check the last N vectors.
            
            # For this MVP refactoring, let's use a simpler counter in self.confirmed_violations
            # But wait, self.confirmed_violations is a set.
            
            # Let's rename/use a counter dict
            if not hasattr(self, 'violation_counters'):
                self.violation_counters = collections.defaultdict(int)
                
            self.violation_counters[track_id] += 1
            
            if self.violation_counters[track_id] >= VIOLATION_PERSISTENCE:
                return True
        else:
            # Reset counter if vehicle corrects itself or is noise
            if hasattr(self, 'violation_counters'):
                self.violation_counters[track_id] = 0
                
        return False
