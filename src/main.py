import os
import sys

# Set working directory to the directory one above the script's directory
print(f"Setting Working Dir to: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.custom_logging.log import Logger
from src.constants.constants import (
    DisplayConstants,
    CameraConstants,
    ObjectDetectionConstants,
    NetworkTableConstants,
    Constants,
)

# run web server that streams video
if DisplayConstants.run_web_server:
    from src.web_interface.web_server import EagleEyeInterface

    web_interface = EagleEyeInterface(lambda _: None)
else:
    web_interface = None

logger = Logger(web_interface)
log = logger.log

import numpy as np
from src.detector import Detector
from src.math_conversions import calculate_local_position, convert_to_global_position, pixels_to_degrees
from time import sleep, time
from threading import Thread, Lock
from networktables import NetworkTables
import struct

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

# As a client to connect to a robot
NetworkTables.initialize(server=NetworkTableConstants.server_address)
game_piece_nt = NetworkTables.getTable("GamePieces")
advantage_kit_nt = NetworkTables.getTable("AdvantageKit")

game_piece_nt.putNumber("active_model", 0)

def time_ms():
    return time() * 1000


class EagleEye:
    def __init__(self):
        model_paths = [
            f"src/models/{model}"
            for model in os.listdir("src/models")
            if not model.endswith(".md") and not model.startswith("_")
        ]
        log(f"Loading models: {model_paths}")
        self.detector = Detector(model_paths, log, Constants.simulation_mode)
        log(f"{len(model_paths)} models loaded")

        self.data = {}
        self.data_lock = Lock()

        detection_threads = []
        for camera in CameraConstants.camera_list:
            t = Thread(target=self.detection_thread, args=(camera,))
            detection_threads.append(t)
            t.start()

        sleep(5)

        log("All threads running")

        game_piece_nt.addEntryListener(self.change_model, key="active_model", immediateNotify=True, localNotify=False)
        game_piece_nt.putStringArray("class_names", list(self.detector.get_class_names().values()))

        while True:
            collected_detections = {}

            for camera in CameraConstants.camera_list:
                with self.data_lock:
                    detections = self.data.get(camera["name"], [])
                    for detection in detections:
                        if detection["class"] not in collected_detections:
                            collected_detections[detection["class"]] = []
                        collected_detections[detection["class"]].append(detection)

            # if no detections, continue
            if len(collected_detections) == 0:
                # reset all values to empty
                for class_name in self.detector.get_class_names().values():
                    game_piece_nt.putNumberArray(f"{class_name}_yaw_angles", [])
                    game_piece_nt.putStringArray(f"{class_name}_local_positions", [])
                    game_piece_nt.putStringArray(f"{class_name}_global_positions", [])
                sleep(0.016)
                continue

            # sort detections by distance using distance
            for class_name, detections in collected_detections.items():
                collected_detections[class_name] = sorted(detections, key=lambda x: x["distance"])

            # remove detections that are too close to each other
            for class_name, detections in collected_detections.items():
                if len(detections) > 1:
                    for i in range(len(detections) - 1):
                        for j in range(i + 1, len(detections)):
                            if np.linalg.norm(detections[i]["local_position"] - detections[j]["local_position"]) < ObjectDetectionConstants.combined_threshold:
                                detections.pop(j)
                                break

            # send detections to network table
            for class_name, detections in collected_detections.items():
                game_piece_nt.putNumberArray(
                    f"{class_name}_yaw_angles",
                    [detection["yaw_angle"] for detection in detections]
                )
                game_piece_nt.putStringArray(
                    f"{class_name}_local_positions",
                    [str(detection["local_position"].tolist()).replace("]", "").replace("[", "") for detection in detections]
                )
                game_piece_nt.putStringArray(
                    f"{class_name}_global_positions",
                    [str(detection["global_position"].tolist()).replace("]", "").replace("[", "") for detection in detections]
                )

            sleep(0.016)

    def detection_thread(self, camera_data):
        log(f"Starting thread for {camera_data['name']} camera")
        self.detector.start_camera(camera_data["camera_id"], camera_data["fov"][0], camera_data["fov"][1], 60)

        while self.detector.ready is False:
            sleep(1)
            log(f"Waiting for {camera_data['name']} camera to be ready")

        while True:
            results, frame_size = self.detector.detect()

            if results is None:
                log(f"{RED}No frame{RESET}", force_no_log=(not Constants.detection_logging))
                sleep(0.02)
                continue

            start_time = time_ms()
            log(f"Speeds: {results.speed}", force_no_log=(not Constants.detection_logging))

            # if no detections, continue
            if not results.boxes:
                with self.data_lock:
                    self.data[camera_data["name"]] = []
                sleep(0.02)
                continue

            detections = []
            debug_points = []

            for box in results.boxes:
                box_class = self.detector.get_class_names()[int(box.cls[0])]
                box_confidence = box.conf.tolist()[0]
                box_lx = box.xyxy.tolist()[0][0]
                box_bottom_center_y = box.xyxy.tolist()[0][3]

                box_rx = box.xyxy.tolist()[0][2]

                box_bottom_center_x = (box_lx + box_rx) / 2

                debug_points.append([int(box_bottom_center_x), int(box_bottom_center_y)])

                # make pixel positions relative to the center
                box_bottom_center_x -= frame_size[0] // 2
                box_bottom_center_y -= frame_size[1] // 2
                box_bottom_center_y = -box_bottom_center_y

                yaw_angle = pixels_to_degrees(box_bottom_center_x, frame_size[0], camera_data["fov"][0], log)
                object_local_position = calculate_local_position(
                    np.array([box_bottom_center_x, box_bottom_center_y]), frame_size, camera_data, log
                )
                robot_pose = np.array(struct.unpack("ddd", advantage_kit_nt.getValue("RealOutputs/Odometry/Robot", np.array([0, 0, 0]))))
                object_global_position = convert_to_global_position(
                    object_local_position, robot_pose
                )

                distance = np.linalg.norm(object_local_position)
                if distance > ObjectDetectionConstants.max_distance:
                    continue

                detections.append({
                    "class": box_class,
                    "confidence": box_confidence,
                    "yaw_angle": yaw_angle,
                    "local_position": object_local_position,
                    "global_position": object_global_position,
                    "distance": distance,
                })

            if DisplayConstants.run_web_server:
                web_interface.set_frame(camera_data["name"], results, debug_points)

            with self.data_lock:
                self.data[camera_data["name"]] = detections

            total_inference_time = sum(results.speed.values()) + (time_ms() - start_time)
            estimated_fps = 1000 / total_inference_time
            log(f"Total processing time (ms): {total_inference_time}", force_no_log=(not Constants.detection_logging))
            log(f"Post processing time (ms): {time_ms() - start_time}", force_no_log=(not Constants.detection_logging))
            log(f"Estimated fps: {estimated_fps}", force_no_log=(not Constants.detection_logging))

    def change_model(self, _, __, value, is_new):
        if is_new:
            self.detector.set_model_index(int(value))


if __name__ == "__main__":
    EagleEye()
