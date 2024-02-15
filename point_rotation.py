import numpy as np


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
