import os
import subprocess

from ultralytics import YOLO
from src.constants.constants import ObjectDetectionConstants
from format_conversion.convert_model import convert_model
from format_conversion.detect_devices import detect_hardware
from custom_logging.log import log


def setup_camera(camera_index, width, height, fps):
    """
    Changes camera settings to the given index, width, height, and fps.
    If an error occurs, it lists available formats.

    :param camera_index: the index of the camera to setup
    :param width: the width of the camera
    :param height: the height of the camera
    :param fps: the fps of the camera
    :return: nothing
    """
    log(f"Setting up camera {camera_index} with width {width}, height {height}, and fps {fps}")

    def run_command(command):
        log(f"Running command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            log(f"Error: {result.stderr.strip()}")
            log("Listing supported formats...")
            os.system("v4l2-ctl --list-formats-ext")
            return False
        return True

    # Set video format
    fmt_command = f"v4l2-ctl -d {camera_index} --set-fmt-video=width={width},height={height},pixelformat=1"
    if not run_command(fmt_command):
        raise Exception("Error setting video format")

    # Set frame rate
    fps_command = f"v4l2-ctl -d {camera_index} --set-parm={fps}"
    run_command(fps_command)


class Detector:
    def __init__(self, model_paths, model_index=0):
        """
        Initializes the detector with the given model paths
        :param model_paths: the paths to the models to use
        :param model_index: the index of the model to use
        """
        self.models = []
        for model_path in model_paths:
            log(f"Loading model from {model_path}")
            self.models.append(YOLO(model_path, task="detect"))
            log(f"Model loaded from {model_path}")
        self.gpu_present, self.tpu_present = detect_hardware()
        self.model_index = model_index

    def set_model_index(self, model_index):
        """
        Sets the index of the model to use
        :param model_index: the index of the model to use
        """
        self.model_index = model_index

    def get_class_names(self):
        """
        Gets the class names of the model
        :return: the class names of the model
        """
        return self.models[self.model_index].names

    def detect(self, camera_index, width, height, fps):
        """
        Detects notes in the given image
        :param camera_index: the index of the camera to use
        :param width: the width of the camera
        :param height: the height of the camera
        :param fps: the fps of the camera
        :return: returns the detections generator
        """
        setup_camera(camera_index, width, height, fps)
        if not self.tpu_present:
            log("Using GPU")
            detections = self.models[self.model_index].predict(
                camera_index,
                show=False,
                device="gpu" if self.gpu_present else "cpu",
                conf=ObjectDetectionConstants.confidence_threshold,
                imgsz=ObjectDetectionConstants.input_size,
                stream=True,
                verbose = False
            )
        else:
            log("Using TPU")
            detections = self.models[self.model_index].predict(
                camera_index,
                show=False,
                conf=ObjectDetectionConstants.confidence_threshold,
                imgsz=ObjectDetectionConstants.input_size,
                stream=True,
                device="tpu:0",
                verbose=False
            )

        return detections
