import cv2

cap = cv2.VideoCapture("test.mp4")  # Change to an actual video file path
if not cap.isOpened():
    print("Error: Cannot open video file.")
else:
    print("Video file opened successfully.")
cap.release()
