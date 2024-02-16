import cv2
from constants import DisplayConstants, CameraConstants, ObjectDetectionConstants
from detector import detect
import numpy as np
from point_rotation import rotate2d
from time import time

# pre-calculate values
width_angle_per_pixel = CameraConstants.camera_width_angle / ObjectDetectionConstants.input_size
height_angle_per_pixel = CameraConstants.camera_height_angle / ObjectDetectionConstants.input_size


def convert_pixels_to_degrees(x, y):
    """
    Converts the given pixel coordinates to degrees
    :param x: the x coordinate (width) from the center of the image
    :param y: the y coordinate (height) from the center of the image
    :return: (x, y) in degrees
    """
    x_angle = width_angle_per_pixel * (ObjectDetectionConstants.input_size / 2 - x)
    y_angle = height_angle_per_pixel * (ObjectDetectionConstants.input_size / 2 - y)

    return -x_angle, y_angle


def calculate_local_note_position(x_angle, y_angle):
    """
    Calculates the position of the note in the local coordinate system
    :param x_angle: the x angle in degrees
    :param y_angle: the y angle in degrees
    :return: the position of the note in the local coordinate system
    """
    # soh cah toa
    x_position = np.tan(90 + x_angle) * CameraConstants.camera_height

    return rotate2d((x_position, 0), np.radians(y_angle))


def convert_to_global_position(local_position, robot_position, robot_angle):
    """
    Converts the local position to the global position
    :param local_position: the local position of the note
    :param robot_position: the position of the robot
    :param robot_angle: the angle of the robot
    :return: the global position of the note
    """
    return np.array(rotate2d(local_position, robot_angle)) + robot_position


def main():
    try:
        # Initialize the camera
        cap = cv2.VideoCapture(0)  # 0 for the default camera, you can change it if you have multiple cameras

        if not cap.isOpened():
            raise ImportError("Could not open video device")

        while True:
            start_time = time()
            # Capture frame-by-frame
            _, frame = cap.read()

            if DisplayConstants.show_output:
                detection, frame = detect(frame, verbose=True, return_image=True)
            else:
                detection = detect(frame, verbose=True, return_image=False)

            for result in detection:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = (
                        int(box.xyxy[0][0].item()),
                        int(box.xyxy[0][1].item()),
                        int(box.xyxy[0][2].item()),
                        int(box.xyxy[0][3].item()),
                    )

                    # get center of the box
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2

                    # convert the center to degrees
                    x_angle, y_angle = convert_pixels_to_degrees(center_x, center_y)

                    print(f"x_angle: {round(x_angle, 2)}, y_angle: {round(y_angle, 2)}")

                    # calculate the local position of the note
                    local_position = calculate_local_note_position(x_angle, y_angle)

                    # convert the local position to the global position
                    global_position = convert_to_global_position(local_position, np.array([0, 0]), 0)

                    print(f"Total frame time: {(time() - start_time) * 1000}ms\n")
                    print(f"Est fps: {1 / (time() - start_time)}\n")
                    print(f"global_position: {global_position}\n")

            if DisplayConstants.show_output:

                # Display the resulting frame
                cv2.imshow('frame', frame)

    except KeyboardInterrupt:
        print("Keyboard interrupt")

        # Release the capture
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
