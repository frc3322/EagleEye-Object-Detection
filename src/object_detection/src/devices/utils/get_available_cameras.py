import glob
import platform
import subprocess

import cv2

# For Windows camera enumeration using DirectShow via pygrabber.
if platform.system() == "Windows":
    import comtypes
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


def get_macos_camera_mapping():
    """
    Uses AVFoundation to get a list of available cameras on macOS.
    Returns:
        dict: Keys are device indices and values are camera names.
    """
    mapping = {}
    try:
        # Use system_profiler to list video devices
        output = subprocess.check_output(
            ["system_profiler", "SPCameraDataType"], universal_newlines=True
        )
        current_name = None
        index = 0
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("Model ID:"):
                current_name = line.split(":")[1].strip()
                mapping[f"Camera {index}"] = current_name
                index += 1
    except Exception as e:
        print("Warning: Unable to run 'system_profiler SPCameraDataType'. Camera names may not be available on macOS.",
              e)
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
    cameras = {}

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

            name = dev_name_mapping.get(device, "Unknown")
            cameras[name] = index

    elif system == "Windows":
        comtypes.CoInitialize()
        graph = FilterGraph()
        device_names = graph.get_input_devices()

        for index, name in enumerate(device_names):
            cameras[name] = index

    elif system == "Darwin":  # macOS
        dev_name_mapping = get_macos_camera_mapping()
        for index, name in enumerate(dev_name_mapping.values()):
            cameras[name] = index

    else:
        # For any other OS, perform a simple index scan.
        for index in range(max_tested):
            cap = cv2.VideoCapture(index)
            if cap is not None and cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    cameras[f"Camera {index}"] = index
                cap.release()

    return cameras


if __name__ == "__main__":
    detected = detect_cameras_with_names()
    if detected:
        print("Detected Cameras:")
        for cam in detected:
            print(f"Index: {detected[cam]}, Name: {cam}")
    else:
        print("No cameras detected.")
