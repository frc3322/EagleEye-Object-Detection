from networktables import NetworkTable
from src.devices.utils.camera import Camera

class Device:
    def __init__(
        self,
        log: callable,
        eagle_eye_nt: NetworkTable,
        device_index: int = 0,
    ):
        self.log = log
        self.eagle_eye_nt = eagle_eye_nt
        self.device_index = device_index

        # Track readiness
        self.ready = False

        # Keep a list of cameras
        self.cameras = []
        self.current_camera = 0

        # Put an initial value for the camera index and listen for changes
        self.eagle_eye_nt.putNumber(f"device:{device_index}_active_camera", 0)
        self.eagle_eye_nt.addEntryListener(
            self._change_camera,
            key=f"device:{device_index}_active_camera",
            immediateNotify=True,
            localNotify=False,
        )

    def _change_camera(self, table, key, value, param) -> None:
        """
        Respond to a NetworkTables entry changing the active camera index.
        Override in child classes if you need a different key format.
        """
        if table == self.eagle_eye_nt and key == f"device:{self.device_index}_active_camera":
            self.set_camera(value)

    def add_camera(self, camera_data: dict) -> None:
        """
        Adds a camera to this device’s camera list
        """
        self.cameras.append(Camera(camera_data, self.log))

    def set_camera(self, camera_index: int) -> None:
        """
        Sets the current camera index
        """
        self.log(f"Changing device:{self.device_index} camera to {camera_index}")
        self.current_camera = int(camera_index)

    def get_camera_index(self) -> int:
        """
        Returns the current camera index
        """
        return self.current_camera

    def get_current_camera(self) -> Camera:
        """
        Returns the current camera object
        """
        return self.cameras[self.current_camera]

    def get_cameras(self) -> list[Camera]:
        """
        Returns all camera objects
        """
        return self.cameras

    def detect(self) -> tuple:
        """
        This should be overridden by any subclass that implements
        actual detection logic.
        """
        raise NotImplementedError("Subclasses must implement the 'detect' method.")

    def get_class_names(self) -> dict[int, str]:
        """
        This should be overridden by any subclass that returns
        class IDs to names mapping.
        """
        raise NotImplementedError("Subclasses must implement 'get_class_names'.")
