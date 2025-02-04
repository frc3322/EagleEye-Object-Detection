import threading
import time
from flask import Flask, Response
import cv2

app = Flask(__name__)

class VideoStreamer:
    def __init__(self):
        self.current_image = cv2.imread("no-signal.jpg")
        self.run_server()

    def update_image(self, new_image):
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2RGBA)
        self.current_image = new_image

    def generate_frames(self):
        while True:
            if self.current_image is not None:
                _, buffer = cv2.imencode(".jpg", self.current_image)
                frame = buffer.tobytes()
                yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"

    def run_server(self):
        @app.route("/")
        def index():
            return Response(
                self.generate_frames(),
                mimetype="multipart/x-mixed-replace; boundary=frame",
            )

class LogStreamer:
    def generate_log(self):
        """Generator that yields new lines from the log file as they are written."""
        while True:
            with open('log.txt', 'r') as log_file:
                log_file.seek(0, 2)  # Move to the end of the file
                while True:
                    line = log_file.readline()
                    if line:
                        yield line
                    else:
                        time.sleep(1)  # Sleep for a second before checking for new content

    @staticmethod
    @app.route('/log')
    def stream_log():
        """Streams the log file content to the client."""
        log_streamer = LogStreamer()
        return Response(log_streamer.generate_log(), content_type='text/plain;charset=utf-8')

def run():
    # Create a thread to run the Flask app
    thread = threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 5000, 'debug': False})
    thread.start()

if __name__ == '__main__':
    # Initialize video streamer and log streamer
    video_streamer = VideoStreamer()
    log_streamer = LogStreamer()
    run()
