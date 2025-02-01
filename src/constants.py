import numpy as np


class NetworkTableConstants:
    server_address = "object-detection.local"

    robot_position_key = "robot_position"
    robot_rotation_key = "robot_rotation"


class ObjectDetectionConstants:
    input_size = 640
    model_path = "model_creation/model.pt"
    confidence_threshold = 0.65

    note_combined_threshold = (
        10  # the threshold for combining notes in the same position
    )


class DisplayConstants:
    show_output = False
    debug = False
    run_web_server = True


class CameraConstants:
    camera_list = [
        {
            "name": "front",
            "camera_id": 0,  # the id of the camera, 0 for the default camera, you can change it if you have multiple
            "camera_width_fov": 70,  # the max view angle in degrees
            "camera_height_fov": 38,  # the max view angle in degrees
            "camera_offset_pos": np.array(
                [0, 0, 73.34]
            ),  # the offset of the camera from the center of the robot in cm
            "camera_pitch": 0,  # the pitch of the camera in degrees
            "camera_yaw": 0,  # the yaw of the camera in degrees
        }
    ]
