import numpy as np


class NetworkTableConstants:
    server_address = "OrangePi2.local"


class ObjectDetectionConstants:
    input_size = 640
    model_path = "model_creation/color_model.onnx"
    confidence_threshold = 0.65

    note_combined_threshold = (
        10  # the threshold for combining notes in the same position
    )


class DisplayConstants:
    show_output = True
    render_output = True
    debug = False
    run_web_server = True


class CameraConstants:
    camera_list = [
        {
            "name": "front",
            "camera_id": 0,  # the id of the camera, 0 for the default camera, you can change it if you have multiple
            "camera_width_angle": 70,  # the max view angle in degrees
            "camera_height_angle": 38,  # the max view angle in degrees
            "camera_offset_pos": np.array(
                [0, 0, 73.34]
            ),  # the offset of the camera from the center of the robot
            # in cm
            "camera_v_angle": 0,  # the angle of the camera from directly forward, positive is up
            "camera_h_angle": 0,  # the angle of the camera from directly forward, positive is right
        }
    ]
