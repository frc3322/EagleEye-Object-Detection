import os
import threading
import time
from threading import Thread
from typing import Any, Generator

import cv2
from flask import (
    Flask,
    send_from_directory,
    request, Response
)

from src.constants.constants import Constants
from src.devices.utils.get_available_cameras import detect_cameras_with_names

with open(os.path.join(".", "assets", "no_image.png"), "rb") as f:  # "./assets/no_image.png"
    no_image = f.read()


def index():
    """
    Serve the index.html file.

    Returns:
        Response: The index.html file.
    """
    return send_from_directory(".", "index.html")


def serve_js():
    """
    Serve the JavaScript file.

    Returns:
        Response: The JavaScript file.
    """
    return send_from_directory("./static", "bundle.js")


def get_available_cameras() -> dict:
    """
    Get a dict of available cameras.

    Returns:
        dict: A dict of available cameras.
    """
    cameras = detect_cameras_with_names()
    return cameras


class EagleEyeInterface:
    def __init__(self, settings_object: Constants | None = None, dev_mode: bool = False):
        """
        Initialize the EagleEyeInterface.

        Starts a Flask server in a separate thread.

        Args:
            settings_object (Constants | None): Optional settings object.
        """
        self.app = Flask(__name__, static_folder=".", static_url_path="")

        self.cameras = get_available_cameras()
        print(f"Detected Cameras: {self.cameras}")
        self.frame_list = {}
        for camera in self.cameras:
            self.frame_list[camera] = None

        self.frame_list_lock = threading.Lock()  # Add a lock for thread-safe access to frame_list

        if settings_object is None:
            self.settings_object = Constants()
        else:
            self.settings_object = settings_object

        self._register_routes()

        self.serve_camera_feed(list(self.cameras.keys())[0], direct_serve=True)

        if dev_mode:
            self.run()
        else:
            # Start Flask server in a separate thread
            self.app_thread = Thread(
                target=self.app.run, kwargs={"host": "0.0.0.0", "port": 5001}, daemon=True
            )
            self.app_thread.start()

    def _register_routes(self) -> None:
        """
        Register all Flask endpoints.
        """
        self.app.add_url_rule("/", "index", index)
        self.app.add_url_rule("/script.js", "script", lambda: serve_js())
        self.app.add_url_rule("/save-settings", "save_settings", self.set_settings, methods=["POST"])
        self.app.add_url_rule("/get-settings", "get_settings", self.get_settings, methods=["GET"])
        self.app.add_url_rule("/get-available-cameras", "get_available_cameras", get_available_cameras, methods=["GET"])

    def run(self) -> None:
        """
        Run the Flask application.
        """
        self.app.run(host="0.0.0.0", port=5001, debug=True,
                     extra_files=["./static/bundle.js", "./style.css", "./index.html"])

    def get_settings(self) -> dict:
        """
        Get the current settings.

        Returns:
            dict: The current settings.
        """
        return self.settings_object.get_config()

    def set_settings(self) -> tuple[dict, int]:
        """
        Set the current settings.

        Returns:
            Response: A success or failure message.
        """
        try:
            settings = request.get_json()  # Extract JSON data from the request
            self.settings_object.load_config_from_json(settings)
            print("Settings updated successfully")
            return {"message": "Settings updated successfully"}, 200
        except Exception as e:
            print("Error updating settings:", e)
            return {"message": "Failed to update settings"}, 500

    def update_camera_frame(self, camera_name: str, frame: bytes) -> None:
        """
        Update the camera frame.

        Args:
            camera_name (str): The ID of the camera.
            frame: The frame to update.
        """
        with self.frame_list_lock:  # Use the lock to ensure thread-safe access
            self.frame_list[camera_name] = frame

    def _frame_generator(self, camera_name: str) -> Generator[bytes, Any, Any]:
        """
        Generate frames for the camera feed.

        Args:
            camera_name (str): The ID of the camera.

        Yields:
            Generator: The camera feed.
        """
        while True:
            time_start = time.time()
            with self.frame_list_lock:  # Use the lock to safely access frame_list
                frame = self.frame_list[camera_name]

            if frame is None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + no_image + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            time.sleep(max((1 / 120) - (time.time() - time_start), 0))

    def serve_camera_feed(self, camera_name: str, direct_serve: bool = False) -> None:
        """
        Serve the camera feed.

        Args:
            camera_name (str): The ID of the camera.
            direct_serve (bool): Whether to directly serve the camera feed.

        Returns:
            Response: The camera feed.
        """
        @self.app.route(f"/feed/{camera_name.replace(' ', '_')}", methods=["GET"])
        def serve_feed():
            return Response(self._frame_generator(camera_name), mimetype='multipart/x-mixed-replace; boundary=frame')

        if direct_serve:
            # Start a thread to update the camera feed
            camera_thread = Thread(target=self._update_camera_feed, args=(camera_name,), daemon=True)
            camera_thread.start()

        print(f"Serving camera feed for {camera_name} at /feed/{camera_name.replace(' ', '_')}")

    def _update_camera_feed(self, camera_name: str) -> None:
        """
        Update the camera feed.

        Args:
            camera_name (str): The ID of the camera.
        """
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        time_start = time.time()
        while True:
            ret, frame = camera.read()
            if not ret:
                break

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # Check if processing time exceeds target frame time
            processing_time = time.time() - time_start
            if processing_time > (1 / 30):
                self.update_camera_frame(camera_name, frame_bytes)
                time_start = time.time()


# Example usage when running this file directly.
if __name__ == "__main__":
    interface = EagleEyeInterface(dev_mode=True)

    while True:
        time.sleep(1)

