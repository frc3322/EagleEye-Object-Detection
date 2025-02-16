from threading import Thread

import cv2
from ultralytics import YOLO
from src.constants.constants import ObjectDetectionConstants, NetworkTableConstants
from src.format_conversion.detect_devices import detect_hardware

latest_frame = None
running = True

def reader_thread(cap):
    global latest_frame
    while running:
        ret, frame = cap.read()
        if not ret:
            break
        latest_frame = frame

class Detector:
    def __init__(self, model_paths, log, simulation_mode, model_index=0):
        """
        Initializes the detector with the given model paths
        :param model_paths: the paths to the models to use
        :param log: the logger to use
        :param simulation_mode: whether to run in simulation mode
        :param model_index: the index of the model to use
        """
        self.models = []
        self.log = log
        self.simulation_mode = simulation_mode
        for model_path in model_paths:
            self.log(f"Loading model from {model_path}")
            self.models.append(YOLO(model_path, task="detect"))
            self.log(f"Model loaded from {model_path}")
        self.gpu_present, self.tpu_present = detect_hardware(self.log)
        self.model_index = model_index

        if self.simulation_mode:
            self.log(f"Running in simulation mode, getting data from: {NetworkTableConstants.server_address}:1181/1?fps=60")

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
        Captures frames directly with OpenCV and runs detection on each frame.
        Yields detection results that mimic the original interface.
        """
        if not self.simulation_mode:
            # Open the video capture device
            cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
            cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FPS, fps)

            if not cap.isOpened():
                raise RuntimeError(f"Error opening camera {camera_index}")

        else:
            cap = cv2.VideoCapture(f"http://{NetworkTableConstants.server_address}:1181/1?fps=60", cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if not cap.isOpened():
                raise RuntimeError(f"Error opening simulation feed from {NetworkTableConstants.server_address}:1181/1?fps=60")

        # Start a thread to read frames from the camera
        reader = Thread(target=reader_thread, args=(cap,))
        reader.start()

        while True:
            # Optionally, convert color if required (e.g., BGR -> RGB)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Run prediction on the captured frame.
            # Note: When passing an image, predict() returns a list, so we extract the first element.
            if not self.tpu_present:
                results = self.models[self.model_index].predict(
                    latest_frame,
                    show=False,
                    device="gpu" if self.gpu_present else "cpu",
                    conf=ObjectDetectionConstants.confidence_threshold,
                    imgsz=ObjectDetectionConstants.input_size,
                    verbose=False
                )
            else:
                results = self.models[self.model_index].predict(
                    latest_frame,
                    show=False,
                    device="tpu:0",
                    conf=ObjectDetectionConstants.confidence_threshold,
                    imgsz=ObjectDetectionConstants.input_size,
                    verbose=False
                )

            # If predict() returns a list, extract the first result.
            if isinstance(results, list):
                results = results[0]

            yield results

        running = False
