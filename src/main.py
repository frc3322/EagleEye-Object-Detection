import os
import sys

# Set working directory to the directory one above the script's directory
print(
    f"Setting Working Dir to: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}"
)
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
from src.devices.google_coral import GoogleCoral
from src.math_conversions import (
    calculate_local_position,
    convert_to_global_position,
    pixels_to_degrees,
)
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
eagle_eye_nt = NetworkTables.getTable("EagleEye")
advantage_kit_nt = NetworkTables.getTable("AdvantageKit")


def time_ms():
    return time() * 1000


class EagleEye:
    def __init__(self):
        model_paths = [
            f"src/models/{model}"
            for model in os.listdir("src/models")
            if not model.endswith(".md") and not model.startswith("_")
        ]
        model_path = model_paths[0]  # only load first found model
        log(f"Loading model: {model_path}")

        # separate cameras based on device
        cameras = {}
        for camera in CameraConstants.camera_list:
            if camera["processing_device"] not in cameras:
                cameras[camera["processing_device"]] = []
            cameras[camera["processing_device"]].append(camera)

        log(f"{len(cameras)} devices found")
        log(f"Cameras: {cameras}")
        log("Starting devices...")

        self.devices = []
        for device, camera_list in cameras.items():
            device = GoogleCoral(
                model_path, log, eagle_eye_nt, len(self.devices)
            )
            for camera in camera_list:
                device.add_camera(camera)
            self.devices.append(device)

        log(f"{len(self.devices)} devices started")

        self.data = {}
        self.data_lock = Lock()

        detection_threads = []
        for device in self.devices:
            t = Thread(target=self.detection_thread, args=(device,))
            detection_threads.append(t)
            t.start()

        class_names = []
        for device in self.devices:
            class_names += list(device.get_class_names().values())

        sleep(1)

        log("All threads running")

        game_piece_nt.putStringArray("class_names", class_names)

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
                for class_name in class_names:
                    game_piece_nt.putNumberArray(f"{class_name}_yaw_angles", [])
                    game_piece_nt.putStringArray(f"{class_name}_local_positions", [])
                    game_piece_nt.putStringArray(f"{class_name}_global_positions", [])
                sleep(0.016)
                continue

            # sort detections by distance using distance
            for class_name, detections in collected_detections.items():
                collected_detections[class_name] = sorted(
                    detections, key=lambda x: x["distance"]
                )

            # remove detections that are too close to each other
            for class_name, detections in collected_detections.items():
                if len(detections) > 1:
                    for i in range(len(detections) - 1):
                        for j in range(i + 1, len(detections)):
                            distance = np.linalg.norm(
                                detections[i]["local_position"]
                                - detections[j]["local_position"]
                            )
                            if distance < ObjectDetectionConstants.combined_threshold:
                                detections.pop(j)
                                break

            # send detections to network table
            for class_name, detections in collected_detections.items():
                game_piece_nt.putNumberArray(
                    f"{class_name}_yaw_angles",
                    [detection["yaw_angle"] for detection in detections],
                )
                game_piece_nt.putStringArray(
                    f"{class_name}_local_positions",
                    [
                        str(detection["local_position"].tolist())
                        .replace("]", "")
                        .replace("[", "")
                        for detection in detections
                    ],
                )
                game_piece_nt.putStringArray(
                    f"{class_name}_global_positions",
                    [
                        str(detection["global_position"].tolist())
                        .replace("]", "")
                        .replace("[", "")
                        for detection in detections
                    ],
                )

            sleep(0.016)

    def detection_thread(self, device: GoogleCoral):
        log(f"Starting thread for {device.get_current_camera().get_name()} camera")
        while True:
            results, frame_size = device.detect()

            if results is None:
                log(
                    f"{RED}No frame{RESET}",
                    force_no_log=(not Constants.detection_logging),
                )
                sleep(0.02)
                continue

            start_time = time_ms()
            log(
                f"Speeds: {results.speed}",
                force_no_log=(not Constants.detection_logging),
            )

            # if no detections, continue
            if not results.boxes:
                with self.data_lock:
                    self.data[device.get_current_camera().get_name()] = []
                if DisplayConstants.run_web_server:
                    web_interface.set_frame(
                        device.get_current_camera().get_name(), results, []
                    )
                sleep(0.02)
                continue

            detections = []
            debug_points = []

            for box in results.boxes:
                box_class = device.get_class_names()[int(box.cls[0])]
                box_confidence = box.conf.tolist()[0]
                box_lx = box.xyxy.tolist()[0][0]
                box_bottom_center_y = box.xyxy.tolist()[0][3]

                box_rx = box.xyxy.tolist()[0][2]

                box_bottom_center_x = (box_lx + box_rx) / 2

                debug_points.append(
                    [int(box_bottom_center_x), int(box_bottom_center_y)]
                )

                # make pixel positions relative to the center
                box_bottom_center_x -= frame_size[0] // 2
                box_bottom_center_y -= frame_size[1] // 2
                box_bottom_center_y = -box_bottom_center_y

                yaw_angle = pixels_to_degrees(
                    box_bottom_center_x,
                    frame_size[0],
                    float(device.get_current_camera().get_fov()[0]),
                    log,
                )
                object_local_position = calculate_local_position(
                    np.array([box_bottom_center_x, box_bottom_center_y]),
                    frame_size,
                    device.get_current_camera().get_fov(),
                    device.get_current_camera().get_camera_offset_pos(),
                    log,
                )
                robot_pose = np.array(
                    struct.unpack(
                        "ddd",
                        advantage_kit_nt.getValue(
                            "RealOutputs/Odometry/Robot", np.array([0, 0, 0])
                        ),
                    )
                )
                object_global_position = convert_to_global_position(
                    object_local_position, robot_pose
                )

                distance = np.linalg.norm(object_local_position)
                if distance > ObjectDetectionConstants.max_distance:
                    continue

                detections.append(
                    {
                        "class": box_class,
                        "confidence": box_confidence,
                        "yaw_angle": yaw_angle,
                        "local_position": object_local_position,
                        "global_position": object_global_position,
                        "distance": distance,
                    }
                )

            if DisplayConstants.run_web_server:
                web_interface.set_frame(
                    device.get_current_camera().get_name(), results, debug_points
                )

            with self.data_lock:
                self.data[device.get_current_camera().get_name()] = detections

            total_inference_time = sum(results.speed.values()) + (
                time_ms() - start_time
            )
            estimated_fps = 1000 / total_inference_time
            log(
                f"Total processing time (ms): {total_inference_time}",
                force_no_log=(not Constants.detection_logging),
            )
            log(
                f"Post processing time (ms): {time_ms() - start_time}",
                force_no_log=(not Constants.detection_logging),
            )
            log(
                f"Estimated fps: {estimated_fps}",
                force_no_log=(not Constants.detection_logging),
            )


if __name__ == "__main__":
    EagleEye()
