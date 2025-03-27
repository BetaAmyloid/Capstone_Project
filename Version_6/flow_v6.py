import os
import time
import numpy as np
import serial
import sys
import cv2
from threading import Thread
from object_detection import ObjectDetection
from near_cherry_cluster import near_cherry_cluster
import json

# Get the directory of the current script (flow_v6.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate to the root directory of the project
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))

# Add RaspberryToArduinoSerial to the system path
raspberry_to_arduino_dir = os.path.join(project_root, 'RaspberryToArduinoSerial')
sys.path.append(raspberry_to_arduino_dir)
from SendToArduino import ArduinoSerial  # IGNORE THE WARNING. IT WILL RUN

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
            time.sleep(0.01)  # Prevents CPU overload
        self.stream.release()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

def find_arduino_ports(start=0, end=5, base_port='/dev/ttyACM', baud_rate=9600):
    """
    Attempts to connect to Arduino devices on serial ports within a given range.
    """
    arduino_ports = []
    for i in range(start, end + 1):
        port_name = f"{base_port}{i}"
        try:
            print(f"Attempting to connect to {port_name}...")
            arduino = ArduinoSerial(port_name, baud_rate)
            arduino_ports.append(arduino)
            print(f"Successfully connected to {port_name}.")
        except serial.SerialException as e:
            print(f"Failed to connect to {port_name}: {e}")
    return arduino_ports

def find_microcontroller_ports(start=0, end=5, baud_rate=9600):
    """
    Attempts to connect to Arduino (ttyACM) and ESP32 (ttyUSB) devices on serial ports within a given range.
    """
    base_ports = ['/dev/ttyACM', '/dev/ttyUSB']  # Support both Arduino and ESP32
    microcontroller_ports = []

    for base_port in base_ports:
        for i in range(start, end + 1):
            port_name = f"{base_port}{i}"
            try:
                print(f"Attempting to connect to {port_name}...")
                microcontroller = ArduinoSerial(port_name, baud_rate)
                microcontroller_ports.append(microcontroller)
                print(f"Successfully connected to {port_name}.")
            except serial.SerialException as e:
                print(f"Failed to connect to {port_name}: {e}")

    return microcontroller_ports

def SendToAllArduino():
    """
    Iterate to each Arduino and ESP32 to send the message
    """

def read_json_data():
    try:
        with open("/home/buslon/Desktop/CoffeeBeanProgram/ImageDetection/Version_6/JSON/controller_V1.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return {"vertical": 1, "horizontal": 1}  # Default values to prevent crashes

if __name__ == '__main__':
    # Find and connect to multiple Arduino devices
    # arduinos = find_arduino_ports(start=0, end=5)
    arduinos = find_microcontroller_ports()
    
    if not arduinos:
        print("No Arduino devices were found. Program terminating...")
        sys.exit()

    detector = ObjectDetection()
    near_cherry_cluster_locator = near_cherry_cluster()
    tracker = cv2.TrackerKCF_create()
    videostream = VideoStream(resolution=(1280, 720), framerate=30).start()

    last_send_time = 0
    prev_horizontal_angle = 90
    prev_vertical_angle = 90

    start_time = time.time()
    
    while True:
        json_data = read_json_data()
        left_or_right = json_data["horizontal"]
        forward_or_backward = json_data["vertical"]

        frame = videostream.read()

        frame_detected_objects, boxes, classes, scores = detector.detect_and_draw(frame)
        cx, cy = near_cherry_cluster_locator.find(boxes, classes, scores)
        cv2.circle(frame, (640, 360), radius=5, color=(0, 255, 0), thickness=1)
        
        if cx is not None and cy is not None:
            AngleHorizontal = np.round(((640 - cx) / 640) * 24.23, 2)
            AngleVertical = np.round(((360 - cy) / 360) * 25.41, 2)
            AbsoluteAH = AngleHorizontal/np.abs(AngleHorizontal)
            AbsoluteVH = AngleVertical/np.abs(AngleVertical)
            current_time = time.time()
            
            if current_time - last_send_time >= 1:

                for arduino in arduinos:
                    #Horizontal Control
                    if -5.0 < AngleHorizontal < 5.0:
                        arduino.Send(message=f'1 {int(prev_horizontal_angle)} 0')
                    else:
                        arduino.Send(message=f'1 {int(prev_horizontal_angle)} 5')

                    #Vertical Control
                    if AbsoluteVH > 0:      #Upward
                        arduino.Send(message=f'2 2 1')
                    if AbsoluteVH < 0:    #Downward
                        arduino.Send(message=f'2 0 1')
                    if -10.0 < AngleVertical < 10.0: 
                        arduino.Send(message=f'2 1 1')

                prev_horizontal_angle += np.round(AbsoluteAH, 2)
                prev_vertical_angle += np.round(AbsoluteVH, 2)

                if prev_horizontal_angle < 0 or prev_horizontal_angle > 180:
                    prev_horizontal_angle = 90

                last_send_time = current_time

            StepsY = int(AngleVertical / 1.8)
            text_position = (cx + 10, cy - 10)
            # cv2.putText(frame, f'({StepsX}, {StepsY})', text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.circle(frame, (cx, cy), radius=5, color=(0, 255, 0), thickness=5)
            cv2.line(frame, pt1=(cx, cy), pt2=(640, 360), color=(0, 255, 0), thickness=1)
        else:
            for arduino in arduinos:
                arduino.Send(message=f'1 {90} 5')

        # Always send movement commands, even if no object is detected
        for arduino in arduinos:
            arduino.Send(message=f'3 {left_or_right} {forward_or_backward} 3000')
            #print(f'Sent Movement Command: 3 {left_or_right} {forward_or_backward} 1000')
        
        

        # if time.time() - start_time >= 3:
        #     # Modify the data (example)
        #     json_data["vertical"] = 1
        #     json_data["horizontal"] = 1

        #     # Write back to JSON
        #     with open("/home/buslon/Desktop/CoffeeBeanProgram/ImageDetection/Version_6/JSON/controller_V1.json", "w") as file:
        #         json.dump(json_data, file, indent=4)
            
        #     start_time = time.time()

        cv2.imshow('Object Detection', frame_detected_objects)

        if cv2.waitKey(1) == ord('q'):
            break
    
    for arduino in arduinos:
        arduino.Close()
    cv2.destroyAllWindows()
    videostream.stop()
