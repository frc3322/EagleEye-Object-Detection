import numpy as np
from scytheautoupdate import check_for_updates
import subprocess
import sys
import os

from detector import Detector
from logging.log import log
from logging.log_server import run
from math_conversions import calculate_local_position, convert_to_global_position, pixels_to_degrees

if not os.path.exists("no_update.txt") and check_for_updates():
    log("Changes have been made to main.py. Restarting the program...")
    subprocess.run([sys.executable, "main.py"])
    sys.exit()

run()
# runs the log server

import cv2
from constants import (
    DisplayConstants,
    CameraConstants,
    ObjectDetectionConstants,
    NetworkTableConstants,
)
from time import sleep
from threading import Thread, Lock
from networktables import NetworkTables

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

# run web server that streams video
if DisplayConstants.run_web_server:
    from web_server import VideoStreamer
    video_streamer = VideoStreamer()

# As a client to connect to a robot
NetworkTables.initialize(server=NetworkTableConstants.server_address)
smart_dashboard = NetworkTables.getTable("SmartDashboard")

smart_dashboard.putNumber("active_model", 0)
smart_dashboard.putBoolean("restart_object_detection", False)


def print_available_cameras():
    for i in range(10):  # Check up to camera index 9 (adjust if needed)
        cap = cv2.VideoCapture(i)
        if not cap.isOpened():
            print(RED + f"Camera index {i} is not available." + RESET)
        else:
            print(GREEN + f"Camera index {i} is available." + RESET)
            cap.release()


def restart():
    log("Restarting the program...")
    subprocess.run([sys.executable, "main.py"])
    sys.exit()


class ScytheVision:
    def __init__(self):
        model_paths = [
            f"models/{model}"
            for model in os.listdir("models")
            if model.endswith(".pt")
        ]
        log(f"Loading models: {model_paths}")
        self.detector = Detector(model_paths)
        log(f"{len(model_paths)} models loaded")

        self.data = {}
        self.data_lock = Lock()

        detection_threads = []
        for camera in CameraConstants.camera_list:
            t = Thread(target=self.detection_thread, args=(camera, self.detector))
            detection_threads.append(t)
            t.start()

        sleep(2)

        log("All threads running")

        smart_dashboard.addEntryListener(self.change_model, key="active_model", immediateNotify=True, flags=NetworkTables.NotifyFlags.UPDATE)
        smart_dashboard.addEntryListener(restart, key="restart_object_detection", immediateNotify=True, flags=NetworkTables.NotifyFlags.UPDATE, localNotify=False)

        while True:
            collected_detections = {}

            for camera in CameraConstants.camera_list:
                with self.data_lock:
                    detections = self.data.get(camera["name"], [])
                    for detection in detections:
                        if detection["class"] not in collected_detections:
                            collected_detections[detection["class"]] = []
                        collected_detections[detection["class"]].append(detection)

            # sort detections by distance using distance
            for class_name, detections in collected_detections.items():
                collected_detections[class_name] = sorted(detections, key=lambda x: x["distance"])

            # remove detections that are too close to each other
            for class_name, detections in collected_detections.items():
                if len(detections) > 1:
                    for i in range(len(detections) - 1):
                        for j in range(i + 1, len(detections)):
                            if np.linalg.norm(detections[i]["local_position"] - detections[j]["local_position"]) < ObjectDetectionConstants.note_combined_threshold:
                                detections.pop(j)
                                break

            # send detections to network table
            for class_name, detections in collected_detections.items():
                smart_dashboard.putNumberArray(
                    f"{class_name}_yaw_angles",
                    [detection["yaw_angle"] for detection in detections]
                )
                smart_dashboard.putNumberArray(
                    f"{class_name}_local_positions",
                    [detection["local_position"].tolist() for detection in detections]
                )
                smart_dashboard.putNumberArray(
                    f"{class_name}_global_positions",
                    [detection["global_position"].tolist() for detection in detections]
                )


    def detection_thread(self, camera_data, detector):
        print(f"Starting thread for {camera_data['name']} camera")
        results_stream = detector.detect()

        detections = []

        for results in results_stream:
            for box in results[0].boxes:
                box_class = self.detector.get_class_names()[int(box.cls[0])]
                box_confidence = box.conf.tolist()[0]
                box_x = box.xywh.tolist()[0][0] * ObjectDetectionConstants.input_size
                box_y = box.xywh.tolist()[0][1] * ObjectDetectionConstants.input_size

                yaw_angle = pixels_to_degrees(np.array([box_x, box_y]), ObjectDetectionConstants.input_size, camera_data)
                object_local_position = calculate_local_position(
                    np.array([box_x, box_y]), ObjectDetectionConstants.input_size, camera_data
                )
                object_global_position = convert_to_global_position(
                    object_local_position, smart_dashboard.getNumberArray("robot_position", [0, 0]), smart_dashboard.getNumber("robot_angle", 0)
                )

                distance = np.linalg.norm(object_local_position)

                detections.append({
                    "class": box_class,
                    "confidence": box_confidence,
                    "yaw_angle": yaw_angle,
                    "local_position": object_local_position,
                    "global_position": object_global_position,
                    "distance": distance,
                })

            with self.data_lock:
                self.data[camera_data["name"]] = detections

    def change_model(self, model_index):
        self.detector.set_model_index(model_index)


if __name__ == "__main__":
    ScytheVision()
