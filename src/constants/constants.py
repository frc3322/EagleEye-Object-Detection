import numpy as np

array = np.array


class Constants:
    def __init__(self):
        pass

    log = False
    print_terminal = True
    detection_logging = False

    simulation_mode = True


class NetworkTableConstants:
    def __init__(self):
        pass

    server_address = "10.0.0.62"
    robot_position_key = "robot_position"
    robot_rotation_key = "robot_rotation"


class ObjectDetectionConstants:
    def __init__(self):
        pass

    input_size = 320
    confidence_threshold = 0.5
    combined_threshold = 0.25  # in meters
    max_distance = 15  # in meters


class DisplayConstants:
    def __init__(self):
        pass

    run_web_server = True


class CameraConstants:
    def __init__(self):
        pass

    camera_list = [
        {
            "name": "front",
            "camera_id": 0,
            "fov": array([70, 38]),
            "camera_offset_pos": array([0.25, 0.0, 0.75]),
            "camera_pitch": 0,
            "camera_yaw": 0,
            "frame_rotation": 0,
            "processing_device": "tpu:0",
            "sim_camera": False,
        },
        {
            "name": "back",
            "camera_id": 1,
            "fov": array([70, 38]),
            "camera_offset_pos": array([0.25, 0.0, 0.75]),
            "camera_pitch": 0,
            "camera_yaw": 180,
            "frame_rotation": 180,
            "processing_device": "tpu:0",
            "sim_camera": False,
        },
    ]
