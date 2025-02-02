import numpy as np
from custom_logging import log


def rotate2d(point, angle):
    """
    Rotate a point around the origin
    :param point: the point to rotate
    :param angle: the angle to rotate the point by
    """
    px, py = point

    sin = np.sin(angle)
    cos = np.cos(angle)

    qx = cos * px - sin * py
    qy = sin * px + cos * py
    return qx, qy

def pixels_to_degrees(pixel_position, total_pixels, fov):
    """
    Converts a pixel position to a degree position
    :param pixel_position: the position in pixels (from the center) np.array([x, y])
    :param total_pixels: the total number of pixels
    :param fov: the field of view of the camera
    :return: the position in degrees (from the center) np.array([x, y])
    """
    pixel_percent = pixel_position / (total_pixels / 2)

    if pixel_percent.any() > 1:
        log("ERROR: Pixel position is greater than total pixels")

    return ((pixel_percent - 0.5) * fov) + 30


def calculate_local_position(
    pixel_position, total_pixels, camera_data
):
    """
    Calculates the local position of the note
    :param pixel_position: the position of the note in pixels (from the center) np.array([x, y])
    :param total_pixels: the total number of pixels
    :param camera_data: the data of the camera
    :return:
    """
    screen_angle = pixels_to_degrees(pixel_position, total_pixels, camera_data["fov"])
    flat_distance = camera_data["camera_offset_pos"][2] / np.arctan(np.radians(screen_angle[1]))
    return rotate2d([0, flat_distance], np.radians(screen_angle[0])) + np.array(camera_data["camera_offset_pos"][:2])


def convert_to_global_position(
    local_position, robot_position, robot_angle
):
    """
    Converts the local position to the field global position
    :param local_position: the local position of the note
    :param robot_position: the position of the robot
    :param robot_angle: the angle of the robot
    :return: the global position of the note
    """
    return rotate2d(local_position - robot_position, robot_angle) + robot_position
