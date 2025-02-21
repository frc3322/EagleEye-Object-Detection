import threading
from threading import Lock

import cv2
import numpy as np
from ultralytics import YOLO
from src.constants.constants import ObjectDetectionConstants, NetworkTableConstants
from src.format_conversion.detect_devices import detect_hardware
from urllib.request import urlopen

latest_frame = None
frame_lock = Lock()


def frame_reader(url):
    global latest_frame
    stream = urlopen(url)
    _bytes = bytearray()
    while True:
        try:
            # Continue reading until we extract a complete JPEG frame
            while True:
                # Flush the buffer if it grows too large
                max_buffer_size = 100000  # adjust as needed
                if len(_bytes) > max_buffer_size:
                    _bytes = _bytes[-max_buffer_size:]

                _bytes += stream.read(4096)
                a = _bytes.find(b'\xff\xd8')  # JPEG start
                b = _bytes.find(b'\xff\xd9')  # JPEG end
                if a != -1 and b != -1:
                    jpg = _bytes[a:b + 2]
                    _bytes = _bytes[b + 2:]
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    if frame is not None:
                        with frame_lock:
                            latest_frame = frame
                    break
        except Exception as e:
            print("Exception in frame_reader:", e)
            break


class Detector:
    def __init__(self, model_paths, log, simulation_mode, model_index=0):
        """
        Initializes the detector with the given model paths
        :param model_paths: the paths to the models to use
        :param log: the logger to use
        :param simulation_mode: whether to run in simulation mode
        :param model_index: the index of the model to use
        """
        self.cap = None
        self.models = []
        self.log = log
        self.simulation_mode = simulation_mode
        for model_path in model_paths:
            self.log(f"Loading model from {model_path}")
            self.models.append(YOLO(model_path, task="detect"))
            self.log(f"Model loaded from {model_path}")
        self.gpu_present, self.tpu_present = detect_hardware(self.log)
        self.model_index = model_index
        self.ready = False

    def set_model_index(self, model_index):
        """
        Sets the index of the model to use
        :param model_index: the index of the model to use
        """
        self.model_index = model_index

    def start_camera(self, camera_index, width, height, fps):
        """
        Initializes the camera or simulation stream.
        """
        if not self.simulation_mode:
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
            self.cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, fps)

            if not self.cap.isOpened():
                raise RuntimeError(f"Error opening camera {camera_index}")
            self.ready = True
        else:
            self.cap = None
            url = f"http://{NetworkTableConstants.server_address}:1181/1?fps=60"
            self.log(f"Using simulation stream at {url}")

            # Start the frame reading thread
            reader_thread = threading.Thread(target=frame_reader, args=(url,), daemon=True)
            reader_thread.start()

            self.ready = True

    def detect(self):
        """
        Captures frames directly and runs detection on each frame.
        """
        global latest_frame

        if not self.simulation_mode:
            ret, frame = self.cap.read()
            if not ret:
                return None, None
        else:
            with frame_lock:
                frame = latest_frame

        if frame is None:
            return None, None

        # Run prediction on the captured frame
        device = "tpu:0" if self.tpu_present else ("gpu" if self.gpu_present else "cpu")
        results = self.models[self.model_index].predict(
            frame,
            show=False,
            device=device,
            conf=ObjectDetectionConstants.confidence_threshold,
            imgsz=ObjectDetectionConstants.input_size,
            verbose=False,
            iou=.5
        )

        frame_width = frame.shape[1]
        frame_height = frame.shape[0]
        frame_size = (frame_width, frame_height)

        return results[0], frame_size

    def get_class_names(self):
        """
        Gets the class names of the model
        :return: the class names of the model
        """
        return self.models[self.model_index].names
