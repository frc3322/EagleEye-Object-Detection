import time
from flask import (
    Flask,
    send_from_directory,
)
from threading import Thread


def index():
    """Serve the index.html file."""
    return send_from_directory(".", "index.html")


def serve_js():
    """Serve the JavaScript file."""
    print("Serving JavaScript file")
    return send_from_directory("./static", "bundle.js")


class EagleEyeInterface:
    def __init__(self):
        """
        Initialize the interface.
        """
        self.app = Flask(__name__, static_folder=".", static_url_path="")

        self._register_routes()

        # Start Flask server in a separate thread
        self.app_thread = Thread(
            target=self.app.run, kwargs={"host": "0.0.0.0", "port": 5001}, daemon=True
        )
        self.app_thread.start()

    def _register_routes(self):
        """Register all Flask endpoints."""
        self.app.add_url_rule("/", "index", index)
        self.app.add_url_rule("/script.js", "script", lambda: serve_js())

    def run(self):
        """Run the Flask application (not used since it's running in a thread)."""
        self.app.run(host="0.0.0.0", port=5000, debug=False)


# Example usage when running this file directly.
if __name__ == "__main__":
    interface = EagleEyeInterface()

    # Keep the main thread alive.
    while True:
        time.sleep(1)