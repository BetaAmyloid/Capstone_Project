import os
import time
import numpy as np
import serial
import sys
import cv2
from threading import Thread
from object_detection import ObjectDetection
from near_cherry_cluster import near_cherry_cluster

class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self, resolution=(640, 480), framerate=30):
        self.stream = cv2.VideoCapture(0)
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.stream.set(3, resolution[0])
        self.stream.set(4, resolution[1])
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while not self.stopped:
            self.grabbed, self.frame = self.stream.read()
        self.stream.release()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

if __name__ == '__main__':

    detector = ObjectDetection(
        #Model_Path = '/home/buslon/Downloads/Despair_2/custom_model_lite',
        Graph_Name = 'tree.tflite',
        Lablemap_Name = 'tree.txt'
    )
    near_cherry_cluster_locator = near_cherry_cluster()
    tracker = cv2.TrackerKCF_create()
    videostream = VideoStream(resolution=(1280, 720), framerate=30).start()

    last_send_time = 0
    prev_horizontal_angle = 90
    prev_vertical_angle = 90
    
    while True:
        frame = videostream.read()

        frame_detected_objects, boxes, classes, scores = detector.detect_and_draw(frame)
        cx, cy = near_cherry_cluster_locator.find(boxes, classes, scores)
        cv2.circle(frame, (640, 360), radius=5, color=(0, 255, 0), thickness=1)
        
        if cx is not None and cy is not None:

            cv2.circle(frame, (cx, cy), radius=5, color=(0, 255, 0), thickness=5)
            cv2.line(frame, pt1=(cx, cy), pt2=(640, 360), color=(0, 255, 0), thickness=1)

        cv2.imshow('Object Detection', frame_detected_objects)

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()
    videostream.stop()