from flask import Flask, Response
import cv2
import threading

app = Flask(__name__)


class VideoStreamer:
    def __init__(self):
        self.current_image = None
        self.run_server()

    def update_image(self, new_image):
        self.current_image = new_image

    def generate_frames(self):
        while True:
            if self.current_image is not None:
                _, buffer = cv2.imencode(".jpg", self.current_image)
                frame = buffer.tobytes()
                yield (
                    b"--frame\r\n",
                    b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n",
                )

    def run_server(self):
        @app.route("/")
        def index():
            return Response(
                self.generate_frames(),
                mimetype="multipart/x-mixed-replace; boundary=frame",
            )

        # Run Flask app in a separate thread
        server_thread = threading.Thread(
            target=app.run, kwargs={"host": "0.0.0.0", "port": 5000, "debug": False}
        )
        server_thread.start()
