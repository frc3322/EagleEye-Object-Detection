import numpy as np


class Constants:
    log = True # Log to file (limits logs to 1 gb)
    print_terminal = False # use for debugging
    detection_logging = False # WILL LOG EVERY DETECTION !!(NOT RECOMMENDED FOR USE)!! !!(OVERRIDES LOG CONSTANT)!!


class NetworkTableConstants:
    server_address = "object-detection.local" # the hostname of this machine

    robot_position_key = "robot_position" # network tables key for robot_position
    robot_rotation_key = "robot_rotation" # network tables key for robot_rotation


class ObjectDetectionConstants:
    input_size = 320 # size of images given to model, needs to be the same as model was trained with
    confidence_threshold = 0.65 # minimum confidence that model needs for detections

    note_combined_threshold = (
        10  # the threshold for combining notes in the same position
    )


class DisplayConstants:
    run_web_server = True


class CameraConstants:
    camera_list = [
        {
            "name": "front",
            "camera_id": 0,  # the id of the camera, 0 for the default camera, you can change it if you have multiple
            "fov": np.array([70, 38]),  # the max view angle in degrees (width, height)
            "camera_offset_pos": np.array(
                [0, 0, 73.34]
            ),  # the offset of the camera from the center of the robot in cm
            "camera_pitch": 0,  # the pitch of the camera in degrees
            "camera_yaw": 0,  # the yaw of the camera in degrees
        }
    ]
