from ultralytics import YOLO
from src.constants.constants import ObjectDetectionConstants
from src.format_conversion.detect_devices import detect_hardware
from src.custom_logging.log import log


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

    def detect(self, camera_index):
        """
        Detects notes in the given image
        :param camera_index: the index of the camera to use
        :return: returns the detections generator
        """
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
