from ultralytics import YOLO
from networktables import NetworkTablesInstance

from src.constants.constants import ObjectDetectionConstants
from src.devices.utils.camera import Camera


class GoogleCoral:
    def __init__(
        self,
        model_path: str,
        log: callable,
        eagle_eye_nt: NetworkTablesInstance,
        device_index: int = 0,
    ):
        """
        Initializes the detector with the given model paths
        :param model_path: the path to the model to use, (tflite_edgetpu format)
        :param log: the logger to use
        :param eagle_eye_nt: the network table to use
        :param device_index: what coral device to use
        """
        self.cap = None
        self.model = None
        self.log = log
        self.device_index = device_index
        self.eagle_eye_nt = eagle_eye_nt

        self.log(f"Loading model from {model_path}")
        self.model = YOLO(model_path, task="detect")
        self.log(f"Model loaded from {model_path}")

        self.ready = False
        self.cameras = []
        self.current_camera = 0

        self.eagle_eye_nt.addEntryListener(
            self.change_model,
            key="active_camera",
            immediateNotify=True,
            localNotify=False,
        )

    def add_camera(self, camera_data: dict) -> None:
        """
        Adds a camera to the detector
        :param camera_data: the data to add the camera with
        """
        self.cameras.append(Camera(camera_data, self.log))

    def set_camera(self, camera_index: int) -> None:
        """
        Sets the current camera index to the given index
        :param camera_index: the index of the camera to set
        """
        self.current_camera = camera_index

    def get_camera_index(self) -> int:
        """
        Gets the current camera index
        """
        return self.current_camera

    def get_current_camera(self) -> Camera:
        """
        Gets the current camera object
        """
        return self.cameras[self.current_camera]

    def get_cameras(self) -> list[Camera]:
        """
        Gets all camera objects
        """
        return self.cameras

    def detect(self) -> tuple:
        """
        Captures frames directly and runs detection on each frame.
        """
        camera = self.get_current_camera()
        frame = camera.get_frame()

        if frame is None:
            return None, None

        # Run prediction on the captured frame
        device = f"tpu:{self.device_index}"
        results = self.model.predict(
            frame,
            show=False,
            device=device,
            conf=ObjectDetectionConstants.confidence_threshold,
            imgsz=ObjectDetectionConstants.input_size,
            verbose=False,
            iou=0.5,
        )

        frame_width = frame.shape[1]
        frame_height = frame.shape[0]
        frame_size = (frame_width, frame_height)

        return results[0], frame_size

    def get_class_names(self) -> dict[int, str]:
        """
        Gets the class names of the model
        :return: the class names of the model
        """
        return self.model.names
