import cv2
import platform
import glob
import subprocess

# For Windows camera enumeration using DirectShow via pygrabber.
if platform.system() == "Windows":
    try:
        from pygrabber.dshow_graph import FilterGraph
    except ImportError:
        raise ImportError("pygrabber is required on Windows. Install with: pip install pygrabber")


def get_linux_camera_mapping():
    """
    Uses v4l2-ctl to get a mapping of video device files to camera names.
    Returns:
        dict: Keys are device file strings (e.g., '/dev/video0') and values are names.
    Note:
        v4l2-ctl must be installed (usually via v4l-utils package).
    """
    mapping = {}
    try:
        # Run v4l2-ctl to list devices
        output = subprocess.check_output(["v4l2-ctl", "--list-devices"], universal_newlines=True)
        # Example output format:
        #  HD Webcam:
        #         /dev/video0
        #         /dev/video1
        #  USB Camera:
        #         /dev/video2
        current_name = None
        for line in output.splitlines():
            # If the line starts without whitespace, it's a device name:
            if line and not line.startswith(" ") and not line.startswith("\t"):
                # Remove colon at end if present
                current_name = line.rstrip(":").strip()
            else:
                # If indented, it's a device node.
                line = line.strip()
                if line.startswith("/dev/video"):
                    mapping[line] = current_name
    except Exception as e:
        print("Warning: Unable to run 'v4l2-ctl --list-devices'. Camera names may not be available on Linux.", e)
    return mapping


def detect_cameras_with_names(max_tested=10):
    """
    Detect available cameras along with their names.
    For Linux, it uses v4l2-ctl to map /dev/video* to friendly names.
    For Windows, it uses pygrabber's FilterGraph to get device names.

    Args:
        max_tested (int): Maximum number of devices to test.

    Returns:
        list of dict: Each dictionary has 'index', 'device' (e.g. '/dev/video0' on Linux or index on Windows),
                      and 'name' (the friendly device name if available).
    """
    system = platform.system()
    cameras = []

    if system == "Linux":
        # Get mapping from device file to name using v4l2-ctl.
        dev_name_mapping = get_linux_camera_mapping()
        # List video devices
        devices = glob.glob("/dev/video*")
        # Sort by the numeric part (e.g. /dev/video0, /dev/video1, …)
        devices.sort(key=lambda x: int(x.replace("/dev/video", "")))
        for device in devices:
            # Convert device file to index (assumes the filename contains the index)
            try:
                index = int(device.replace("/dev/video", ""))
            except ValueError:
                continue
            # Try opening the device to verify it's working
            cap = cv2.VideoCapture(index)
            if cap is not None and cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    # Fetch name from mapping if available; if not, fallback to 'Unknown'
                    name = dev_name_mapping.get(device, "Unknown")
                    cameras.append({"index": index, "device": device, "name": name})
                cap.release()

    elif system == "Windows":
        # Use pygrabber to list available DirectShow video devices.
        graph = FilterGraph()
        device_names = graph.get_input_devices()  # This returns a list of friendly names.
        # Iterate through indices (sometimes there may be gaps so we test up to max_tested)
        for index in range(max_tested):
            cap = cv2.VideoCapture(index)
            if cap is not None and cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    # Map index to name if available from pygrabber.
                    # Note: Device ordering in pygrabber usually matches the index order,
                    # but if index >= len(device_names) we fallback.
                    name = device_names[index] if index < len(device_names) else "Unknown"
                    cameras.append({"index": index, "device": index, "name": name})
                cap.release()
    else:
        # For any other OS, perform a simple index scan.
        for index in range(max_tested):
            cap = cv2.VideoCapture(index)
            if cap is not None and cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    cameras.append({"index": index, "device": index, "name": "Unknown"})
                cap.release()

    return cameras


if __name__ == "__main__":
    detected = detect_cameras_with_names()
    if detected:
        print("Detected Cameras:")
        for cam in detected:
            print(f"Index: {cam['index']}, Device: {cam['device']}, Name: {cam['name']}")
    else:
        print("No cameras detected.")
