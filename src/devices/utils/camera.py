import threading
from urllib.request import urlopen

import cv2
import numpy as np

from src.constants.constants import NetworkTableConstants


def sim_frame_reader(url, latest_frame_method):
    """
    Reads frames from a simulated camera stream.

    This function continuously reads JPEG frames from a given URL and decodes them.
    The decoded frames are then passed to the provided method for further processing.
    This method prevents buffer issues with other methods.

    :param url: The URL of the simulated camera stream.
    :param latest_frame_method: A callable that processes the latest frame.
    """
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
                a = _bytes.find(b"\xff\xd8")  # JPEG start
                b = _bytes.find(b"\xff\xd9")  # JPEG end
                if a != -1 and b != -1:
                    jpg = _bytes[a : b + 2]
                    _bytes = _bytes[b + 2 :]
                    frame = cv2.imdecode(
                        np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR
                    )
                    if frame is not None:
                        latest_frame_method(frame)
                    break
        except Exception as e:
            print("Exception in frame_reader:", e)
            break


class Camera:
    def __init__(self, camera_data: dict, log: callable):
        """
        Initializes the camera with the given data (dict)
        :param camera_data: the data to initialize the camera with
        """
        self.name = camera_data["name"]
        self.camera_id = camera_data["camera_id"]
        self.fov = camera_data["fov"]
        self.camera_offset_pos = camera_data["camera_offset_pos"]
        self.camera_pitch = camera_data["camera_pitch"]
        self.camera_yaw = camera_data["camera_yaw"]
        self.processing_device = camera_data["processing_device"]
        self.sim_camera = camera_data["sim_camera"]
        self.frame_rotation = camera_data["frame_rotation"]

        self.log = log

        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.cap = None

        self._start_camera()

    def _start_camera(self) -> None:
        """
        Starts the camera with the given camera data
        """
        if not self.sim_camera:
            self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_V4L2)
            self.cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.fov[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.fov[1])
            self.cap.set(cv2.CAP_PROP_FPS, 60)

            if not self.cap.isOpened():
                raise RuntimeError(f"Error opening camera {self.camera_id}")
        else:
            url = f"http://{NetworkTableConstants.server_address}:1181/{self.camera_id}?fps=60"
            self.log(f"Using simulation stream at {url}")

            # Start the frame reading thread
            reader_thread = threading.Thread(
                target=sim_frame_reader, args=(url, self._set_frame), daemon=True
            )
            reader_thread.start()

    def get_frame(self) -> np.ndarray | None:
        """
        Gets the latest frame from the camera
        """
        if not self.sim_camera:
            ret, frame = self.cap.read()
            if not ret:
                return None
            frame = cv2.rotate(frame, self.frame_rotation)
            return frame
        else:
            with self.frame_lock:
                return cv2.rotate(self.latest_frame, self.frame_rotation)

    def _set_frame(self, frame) -> None:
        """
        Sets the latest frame from the camera
        """
        with self.frame_lock:
            self.latest_frame = frame

    def get_processing_device(self) -> str:
        """
        Gets the processing device for the camera
        """
        return self.processing_device

    def get_camera_offset_pos(self) -> np.ndarray:
        """
        Gets the camera offset position
        """
        return self.camera_offset_pos

    def get_camera_pitch(self) -> float:
        """
        Gets the camera pitch
        """
        return self.camera_pitch

    def get_camera_yaw(self) -> float:
        """
        Gets the camera yaw
        """
        return self.camera_yaw

    def get_fov(self) -> np.ndarray:
        """
        Gets the field of view of the camera
        """
        return self.fov

    def get_name(self) -> str:
        """
        Gets the name of the camera
        """
        return self.name
