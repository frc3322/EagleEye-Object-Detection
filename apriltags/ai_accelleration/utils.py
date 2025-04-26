from typing import Union

import cv2
import numpy as np
from PIL import Image

# Shared constants
SCALE_FACTOR = 0.30
CONF_THRESHOLD = 0.4
MIN_GROUP_SIZE = 2
VIDEO_PATH = "test.mp4"
MODEL_PATH = "model.pth"


def scale_with_aspect(
        img: Union[Image.Image, np.ndarray], scale_factor: float
) -> Union[Image.Image, np.ndarray]:
    """
    Scale an image while maintaining aspect ratio.

    Args:
        img: Either a PIL Image or a numpy array (OpenCV image)
        scale_factor: Scale factor to apply

    Returns:
        Scaled image in the same format as the input
    """
    if isinstance(img, Image.Image):
        w, h = img.size
        new_w, new_h = int(w * scale_factor), int(h * scale_factor)
        return img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    else:
        h, w = img.shape[:2]
        new_w, new_h = int(w * scale_factor), int(h * scale_factor)
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


class ScaleTransform:
    """Torchvision transform for scaling PIL images by a factor."""

    def __init__(self, scale_factor: float):
        self.scale_factor = scale_factor

    def __call__(self, img: Image.Image) -> Image.Image:
        return scale_with_aspect(img, self.scale_factor)


def calculate_crop_regions_from_grid(
        conf_grid_mask: np.ndarray, cell_w: int, cell_h: int
) -> list:
    """
    Calculate the crop regions based on the connected components in the grid mask.

    Args:
        conf_grid_mask (np.ndarray): The binary mask of the grid.
        cell_w (int): Width of each cell in pixels.
        cell_h (int): Height of each cell in pixels.

    Returns:
        list: A list of tuples representing the crop regions (x0, y0, x1, y1).
    """
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        conf_grid_mask.astype(np.uint8), 8, cv2.CV_32S
    )

    regions = []

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]

        if area >= MIN_GROUP_SIZE:
            x_min_cell = stats[i, cv2.CC_STAT_LEFT]
            y_min_cell = stats[i, cv2.CC_STAT_TOP]
            width_cells = stats[i, cv2.CC_STAT_WIDTH]
            height_cells = stats[i, cv2.CC_STAT_HEIGHT]

            x0_pixel = x_min_cell * cell_w
            y0_pixel = y_min_cell * cell_h
            x1_pixel = (x_min_cell + width_cells) * cell_w
            y1_pixel = (y_min_cell + height_cells) * cell_h

            regions.append((x0_pixel, y0_pixel, x1_pixel, y1_pixel))
    return regions
