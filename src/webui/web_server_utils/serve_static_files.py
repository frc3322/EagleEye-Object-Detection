from flask import send_from_directory


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
