import cv2
import time

class ObjectTracker:
    def __init__(self, frame, initial_bounding_box):
        self.tracker = cv2.TrackerKCF_create()
        self.initial_bounding_box = initial_bounding_box
        self.init_tracker(frame, initial_bounding_box)

    def init_tracker(self, frame, bbox):
        ret = self.tracker.init(frame, bbox)
        if not ret:
            print("Failed to initialize tracker")

    def track(self, frame):
        ret, bbox = self.tracker.update(frame)
        # Draw bounding box
        if ret:
            point1 = (int(bbox[0]), int(bbox[1]))
            point2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, point1, point2, (255, 0, 0), 2, 1)
        else:
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        # Display result
        cv2.putText(frame, "KCF Tracker", (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)
        return frame

