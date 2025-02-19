import time
import queue
import numpy as np
from flask import Flask, Response, request, jsonify, send_from_directory, stream_with_context
from threading import Thread
import cv2
from threading import Lock

def index():
    """Serve the index.html file."""
    return send_from_directory('.', 'index.html')

def serve_static(filename):
    """Serve other static files such as style.css and script.js."""
    return send_from_directory('.', filename)

def convert_ndarray_to_bytes(image: np.ndarray) -> bytes:
    """Convert a numpy image array to JPEG-encoded bytes."""
    _, buffer = cv2.imencode('.jpg', image)
    return buffer.tobytes()

class EagleEyeInterface:
    def __init__(self, settings_update_callback):
        """
        Initialize the interface.

        :param settings_update_callback: a function to call when settings are updated.
        """
        self.settings_update_callback = settings_update_callback
        self.app = Flask(__name__, static_folder='.', static_url_path='')
        self.settings = {}
        self.log_queue = queue.Queue()
        self.camera_frames = {}  # Dictionary mapping camera name to frame (bytes)

        # Replace the queue with a direct buffer
        self.frame_buffer = {}  # Holds latest frames before processing
        self.frame_lock = Lock()

        # Start the processing thread
        self.frame_thread = Thread(target=self._process_frame_queue, daemon=True)
        self.frame_thread.start()

        self._register_routes()

        # Start Flask server in a separate thread
        self.app_thread = Thread(target=self.app.run, kwargs={'host': '0.0.0.0', 'port': 5000}, daemon=True)
        self.app_thread.start()

    def _register_routes(self):
        """Register all Flask endpoints."""
        self.app.add_url_rule('/', 'index', index)
        self.app.add_url_rule('/<path:filename>', 'serve_static', serve_static)
        self.app.add_url_rule('/update_settings', 'update_settings', self.update_settings, methods=['POST'])
        self.app.add_url_rule('/video_feed/<camera_name>', 'video_feed', self.video_feed)
        self.app.add_url_rule('/log_stream', 'log_stream', self.log_stream)
        self.app.add_url_rule('/available_cameras', 'available_cameras', self.available_cameras)

    def update_settings(self):
        """Endpoint called when settings are updated via POST."""
        data = request.get_json()
        if data:
            self.settings.update(data)
            self.log_message("Settings updated: " + str(data))
            self.settings_update_callback(data)
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    def generate_frames(self, camera_name):
        """Generator that yields camera frames."""
        while True:
            frame = self.camera_frames.get(camera_name)
            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                time.sleep(0.1)

    def video_feed(self, camera_name):
        """Endpoint to stream video frames for a given camera."""
        return Response(self.generate_frames(camera_name),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    def log_stream(self):
        """Endpoint to stream log messages to the client via Server-Sent Events."""
        def event_stream():
            while True:
                try:
                    message = self.log_queue.get(timeout=1)
                    yield f"data: {message}\n\n"
                except queue.Empty:
                    yield ": heartbeat\n\n"
        return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

    def log_message(self, message):
        """Add a message to the log."""
        self.log_queue.put(message)

    def set_frame(self, camera_name, results, points):
        """
        Store the latest frame in a buffer and let the background thread process it.
        This minimizes time spent in the main thread.
        """
        with self.frame_lock:
            self.frame_buffer[camera_name] = [results, points]

    def _process_frame_queue(self):
        """
        Continuously process frames from frame_buffer and update camera_frames.
        Only the latest frame per camera is stored, avoiding queue buildup.
        """
        while True:
            with self.frame_lock:
                buffer_copy = self.frame_buffer.copy()
                self.frame_buffer.clear()

            for camera_name, data in buffer_copy.items():
                frame, points = data
                frame = frame.plot()

                if len(points) > 0:
                    for point in points:
                        cv2.circle(frame, point, 5, (0, 255, 0), 4)

                if isinstance(frame, np.ndarray):
                    frame = convert_ndarray_to_bytes(frame)
                self.camera_frames[camera_name] = frame

            time.sleep(0.01)  # Small sleep to prevent busy looping

    def available_cameras(self):
        """Returns a JSON list of available camera names."""
        return jsonify(list(self.camera_frames.keys()))

    def run(self):
        """Run the Flask application (not used since it's running in a thread)."""
        self.app.run(host='0.0.0.0', port=5000, debug=False)

# Example usage when running this file directly.
if __name__ == '__main__':
    def settings_callback(updated_settings):
        print("Callback: Settings were updated:", updated_settings)

    interface = EagleEyeInterface(settings_callback)
    interface.log_message("Interface initialized and ready.")

    # Set up available cameras (adjust camera IDs as needed)
    camera_list = {
        'front_camera': 0,
    }
    caps = {name: cv2.VideoCapture(idx) for name, idx in camera_list.items()}

    def capture_loop():
        """Continuously capture frames from all cameras."""
        while True:
            for name, cap in caps.items():
                ret, frame = cap.read()
                if ret:
                    interface.set_frame(name, frame)
            time.sleep(0.1)

    capture_thread = Thread(target=capture_loop, daemon=True)
    capture_thread.start()

    # Keep the main thread alive.
    while True:
        time.sleep(1)
