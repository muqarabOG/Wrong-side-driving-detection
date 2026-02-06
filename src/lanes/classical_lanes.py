import cv2
import numpy as np
import cv2
import numpy as np
from config import ROI_POINTS

class ClassicalLaneDetector:
    def __init__(self, frame_width, frame_height):
        self.width = frame_width
        self.height = frame_height
        
        # Calculate source points for perspective transform based on ROI_POINTS config
        # ROI_POINTS is percentage of (w, h)
        self.src_points = np.float32([
            [int(ROI_POINTS[0][0] * frame_width), int(ROI_POINTS[0][1] * frame_height)],
            [int(ROI_POINTS[1][0] * frame_width), int(ROI_POINTS[1][1] * frame_height)],
            [int(ROI_POINTS[2][0] * frame_width), int(ROI_POINTS[2][1] * frame_height)],
            [int(ROI_POINTS[3][0] * frame_width), int(ROI_POINTS[3][1] * frame_height)]
        ])
        
        # Dest points - Warp to a rectangle (Bird's Eye View)
        # We want the lane to appear parallel
        offset_x = frame_width * 0.2
        self.dst_points = np.float32([
            [offset_x, 0],
            [frame_width - offset_x, 0],
            [frame_width - offset_x, frame_height],
            [offset_x, frame_height]
        ])
        
        self.M = cv2.getPerspectiveTransform(self.src_points, self.dst_points)
        self.Minv = cv2.getPerspectiveTransform(self.dst_points, self.src_points)

    def warp_frame(self, frame):
        return cv2.warpPerspective(frame, self.M, (self.width, self.height))

    def detect_lines(self, frame):
        """
        Return a mask of detected lines.
        """
        # HLS Color space is better for color selection
        hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
        
        # White color mask
        lower_white = np.array([0, 200, 0])
        upper_white = np.array([255, 255, 255])
        white_mask = cv2.inRange(hls, lower_white, upper_white)
        
        # Yellow color mask
        lower_yellow = np.array([10, 0, 100])
        upper_yellow = np.array([40, 255, 255])
        yellow_mask = cv2.inRange(hls, lower_yellow, upper_yellow)
        
        combined_mask = cv2.bitwise_or(white_mask, yellow_mask)
        
        return combined_mask

    def get_lane_polygon(self, frame):
        """
        Simple MVP: Return the warped ROI polygon for visualization or logic.
        In a real scenario, this would fit polynomials to the lines.
        """
        # For MVP, we presume the 'lane' is roughly the detected ROI.
        # We can analyze the warped image to find 'up' vs 'down' lanes if we had a divider.
        # But for 'Wrong Side', we essentially need to know:
        # 1. Where are the lanes?
        # 2. What is the direction of EACH lane?
        
        # This is hard without a known map or clear divider detection.
        # For the MVP, let's assume a standard two-lane road where:
        # Left half = Moving Down (Approaching)
        # Right half = Moving Up (Departing)
        # OR configurable via map.
        
        detected_mask = self.detect_lines(frame)
        warped_mask = self.warp_frame(detected_mask)
        
        return warped_mask, self.src_points
