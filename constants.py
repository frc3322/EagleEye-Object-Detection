class NetworkTableConstants:
    server_address = ""


class ObjectDetectionConstants:
    input_size = 640
    model_path = "model_creation/color_model.onnx"
    confidence_threshold = 0.65


class DisplayConstants:
    show_output = True


class CameraConstants:
    camera_width_angle = 110  # the max view angle in degrees
    camera_height_angle = 85  # the max view angle in degrees

    camera_height = 10  # the height of the camera from the ground in cm
