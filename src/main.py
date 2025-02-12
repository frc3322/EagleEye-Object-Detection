import os
import sys

# Set working directory to the directory one above the script's directory
print(f"Setting Working Dir to: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from detector import Detector
from custom_logging.log import log
from math_conversions import calculate_local_position, convert_to_global_position, pixels_to_degrees

from src.constants.constants import (
    DisplayConstants,
    CameraConstants,
    ObjectDetectionConstants,
    NetworkTableConstants,
    Constants,
)
from time import sleep, time
from threading import Thread, Lock
from networktables import NetworkTables

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

# run web server that streams video
if DisplayConstants.run_web_server:
    from web_server import VideoStreamer, LogStreamer, run

    video_streamer = VideoStreamer()
    log_streamer = LogStreamer()
    run()

# As a client to connect to a robot
NetworkTables.initialize(server=NetworkTableConstants.server_address)
smart_dashboard = NetworkTables.getTable("SmartDashboard")

smart_dashboard.putNumber("active_model", 0)
smart_dashboard.putBoolean("restart_object_detection", False)


class EagleEye:
    def __init__(self):
        model_paths = [
            f"src/models/{model}"
            for model in os.listdir("src/models")
            if not model.endswith(".md") and not model.startswith("_")
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

        smart_dashboard.addEntryListener(self.change_model, key="active_model", immediateNotify=True, localNotify=False)

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

            sleep(0.1)


    def detection_thread(self, camera_data, detector):
        log(f"Starting thread for {camera_data['name']} camera")
        results_stream = detector.detect(camera_data["camera_id"], camera_data["fov"][0], camera_data["fov"][1], 60)

        detections = []

        for results in results_stream:
            start_time = time()
            log(f"Speeds: {results.speed}", force_no_log=Constants.detection_logging)
            video_streamer.update_image(results.plot())

            for box in results.boxes:
                box_class = self.detector.get_class_names()[int(box.cls[0])]
                box_confidence = box.conf.tolist()[0]
                box_x = box.xywh.tolist()[0][0] * ObjectDetectionConstants.input_size
                box_y = box.xywh.tolist()[0][1] * ObjectDetectionConstants.input_size

                yaw_angle = pixels_to_degrees(np.array([box_x, box_y]), ObjectDetectionConstants.input_size, camera_data["fov"])
                object_local_position = calculate_local_position(
                    np.array([box_x, box_y]), ObjectDetectionConstants.input_size, camera_data
                )
                object_global_position = convert_to_global_position(
                    object_local_position, smart_dashboard.getNumberArray("robot_position", np.array([0, 0])), smart_dashboard.getNumber("robot_angle", 0)
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

            total_inference_time = sum(results.speed.values()) + (time() - start_time)
            estimated_fps = 1000 / total_inference_time
            log(f"Total processing time (ms): {total_inference_time}", force_no_log=Constants.detection_logging)
            log(f"Estimated fps: {estimated_fps}", force_no_log=Constants.detection_logging)

    def change_model(self, _, __, value, is_new):
        if is_new:
            self.detector.set_model_index(int(value))


if __name__ == "__main__":
    EagleEye()
