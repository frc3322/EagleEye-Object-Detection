import numpy as np

array = np.array


class Constants:
    log = False
    print_terminal = True
    detection_logging = False

    simulation_mode = True


class NetworkTableConstants:
    server_address = "10.0.0.62"
    robot_position_key = "robot_position"
    robot_rotation_key = "robot_rotation"


class ObjectDetectionConstants:
    input_size = 320
    confidence_threshold = 0.5
    combined_threshold = 0.25  # in meters
    max_distance = 15  # in meters


class DisplayConstants:
    run_web_server = True


class CameraConstants:
    camera_list = [
        {
            "name": "front",
            "camera_id": 0,
            "fov": array([70, 38]),
            "camera_offset_pos": array([0.25, 0.0, 0.75]),
            "camera_pitch": 0,
            "camera_yaw": 0,
            "processing_device": "0",
            "sim_camera": True,
        },
        {
            "name": "front",
            "camera_id": 1,
            "fov": array([70, 38]),
            "camera_offset_pos": array([0.25, 0.0, 0.75]),
            "camera_pitch": 0,
            "camera_yaw": 0,
            "processing_device": "0",
            "sim_camera": True,
        }
    ]
