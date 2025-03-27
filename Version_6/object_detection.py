######## Webcam Object Detection Using Tensorflow-trained Classifier #########
#
# Author: Evan Juras
# Date: 10/27/19
# Description: 
# This program uses a TensorFlow Lite model to perform object detection on a live webcam
# feed. It draws boxes and scores around the objects of interest in each frame from the
# webcam. To improve FPS, the webcam object runs in a separate thread from the main program.
# This script will work with either a Picamera or regular USB webcam.
#
# This code is based off the TensorFlow Lite image classification example at:
# https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/examples/python/label_image.py
#
# I added my own method of drawing boxes and labels using OpenCV.

# Import packages
import os
import argparse
import cv2
import numpy as np
import sys
import time
from threading import Thread
import importlib.util
import sys

class ObjectDetection:
    def __init__(self, 
                 Model_Path='/home/buslon/Desktop/CoffeeBeanProgram/ImageDetection/custom_model_lite', 
                 Graph_Name='detect.tflite', 
                 Lablemap_Name='labelmap.txt', 
                 Threshold=0.5, 
                 Width=1280, 
                 Height=720):
        self.MODEL_NAME = Model_Path
        self.GRAPH_NAME = Graph_Name
        self.LABELMAP_NAME = Lablemap_Name
        self.min_conf_threshold = Threshold
        self.imW = Width
        self.imH = Height
        self.BackgroundColor = [ (14,79,193),       #Overipe
                                (0,255,20),         #Ripe 
                                (15,255,250)        #Unripe
                                ]

        # Import TensorFlow libraries
        pkg = importlib.util.find_spec('tflite_runtime')
        if pkg:
            from tflite_runtime.interpreter import Interpreter
        else:
            from tensorflow.lite.python.interpreter import Interpreter

        # Get path to current working directory
        self.CWD_PATH = os.getcwd()

        # Path to .tflite file, which contains the model that is used for object detection
        self.PATH_TO_CKPT = os.path.join(self.CWD_PATH, self.MODEL_NAME, self.GRAPH_NAME)

        # Path to label map file
        self.PATH_TO_LABELS = os.path.join(self.CWD_PATH, self.MODEL_NAME, self.LABELMAP_NAME)

        # Load the label map
        self.labels = self.load_labels()

        # Load the TensorFlow Lite model.
        self.interpreter = Interpreter(model_path=self.PATH_TO_CKPT)
        self.interpreter.allocate_tensors()

        # Get model details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]

        self.floating_model = (self.input_details[0]['dtype'] == np.float32)

        self.input_mean = 127.5
        self.input_std = 127.5

        # Check output layer name to determine if this model was created with TF2 or TF1
        self.outname = self.output_details[0]['name']

        if 'StatefulPartitionedCall' in self.outname:  # This is a TF2 model
            self.boxes_idx, self.classes_idx, self.scores_idx = 1, 3, 0
        else:  # This is a TF1 model
            self.boxes_idx, self.classes_idx, self.scores_idx = 0, 1, 2

        # Initialize frame rate calculation
        self.frame_rate_calc = 1
        self.freq = cv2.getTickFrequency()

    def load_labels(self):
        """
        Load label map from file.
        """
        try:
            with open(self.PATH_TO_LABELS, 'r') as f:
                labels = [line.strip() for line in f.readlines()]
            if labels[0] == '???':
                del(labels[0])
            return labels
        except Exception as e:
            print(f"Error loading labels: {e}")
            return []

    def detect_objects(self, frame):
        """
        Detect objects in the frame.
        """
        # Resize and preprocess the frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (self.width, self.height))
        input_data = np.expand_dims(frame_resized, axis=0)

        if self.floating_model:
            input_data = (np.float32(input_data) - self.input_mean) / self.input_std

        # Perform detection
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()

        # Retrieve detection results
        boxes = self.interpreter.get_tensor(self.output_details[self.boxes_idx]['index'])[0]
        classes = self.interpreter.get_tensor(self.output_details[self.classes_idx]['index'])[0]
        scores = self.interpreter.get_tensor(self.output_details[self.scores_idx]['index'])[0]

        return boxes, classes, scores

    def draw_results(self, frame, boxes, classes, scores):
        """
        Draw detection results on the frame.
        """
        for i in range(len(scores)):
            if (scores[i] > self.min_conf_threshold) and (scores[i] <= 1.0):
                ymin = int(max(1, (boxes[i][0] * self.imH)))
                xmin = int(max(1, (boxes[i][1] * self.imW)))
                ymax = int(min(self.imH, (boxes[i][2] * self.imH)))
                xmax = int(min(self.imW, (boxes[i][3] * self.imW)))

                object_name = self.labels[int(classes[i])]
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), self.BackgroundColor[int(classes[i])], 2)
                label = f'{object_name}: {int(scores[i] * 100)}% ID: {i}'
                label_size, base_line = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                label_ymin = max(ymin, label_size[1] + 10)
                cv2.rectangle(frame, (xmin, label_ymin - label_size[1] - 10), 
                              (xmin + label_size[0], label_ymin + base_line - 10), 
                              (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                            (0, 0, 0), 2)
        return frame

    def detect_and_draw(self, frame):
        """
        Perform object detection and draw results on the frame.
        """
        t1 = cv2.getTickCount()
        boxes, classes, scores = self.detect_objects(frame)
        self.draw_results(frame, boxes, classes, scores)
        t2 = cv2.getTickCount()
        time1 = (t2 - t1) / self.freq
        self.frame_rate_calc = 1 / time1
        cv2.putText(frame, f'FPS: {self.frame_rate_calc:.2f}', (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                    (255, 255, 0), 2, cv2.LINE_AA)
        return frame, boxes, classes, scores
    
    # def detect_and_getBounding_boxes():

