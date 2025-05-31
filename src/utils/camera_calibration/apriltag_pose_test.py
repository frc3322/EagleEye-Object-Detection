import json
import os
from typing import Tuple

import cv2
import numpy as np
from pupil_apriltags import Detector

from src.apriltags.utils.fmap_parser import load_fmap_file


def load_camera_parameters(json_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Load camera matrix and distortion coefficients from a JSON file."""
    with open(json_path, "r") as file:
        data = json.load(file)
    camera_matrix = np.array(data["camera_matrix"], dtype=np.float64)
    distortion_coefficients = np.array(
        data["distortion_coefficients"], dtype=np.float64
    )
    return camera_matrix, distortion_coefficients


def main() -> None:
    camera_json_path = os.path.join(os.path.dirname(__file__), "camera_intrinsics.json")
    test_image_path = os.path.join(os.path.dirname(__file__), "apriltag_test.png")

    camera_matrix, distortion_coefficients = load_camera_parameters(camera_json_path)

    image = cv2.imread(test_image_path)
    if image is None:
        raise RuntimeError(f"Could not load image: {test_image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    detector = Detector(families="tag36h11")
    tags = detector.detect(gray)

    fmap_file_path = "E:/Ceph-Mirror/Python-Files/Projects/FIRST-Note-Detection/src/apriltags/utils/frc2025r2.json"
    apriltag_data = load_fmap_file(fmap_file_path)

    image_points_list = []
    object_points_list = []

    for tag in tags:
        image_points_list.extend(tag.corners.astype(np.float32))

        if tag.tag_id in apriltag_data:
            object_points_list.extend(
                apriltag_data[tag.tag_id].global_corners.astype(np.float32)
            )
        else:
            print(f"Tag {tag.tag_id} not found in fmap file")

    for idx, image_point in enumerate(image_points_list):
        print(f"image_point {idx}: {image_point}")
        print(f"object_point {idx}: {object_points_list[idx]}")

    image_points = np.array(image_points_list, dtype=np.float32).reshape(-1, 2)
    object_points = np.array(object_points_list, dtype=np.float32).reshape(-1, 3)

    success, rvec, tvec = cv2.solvePnP(
        object_points, image_points, camera_matrix, distortion_coefficients
    )

    rotation_matrix, _ = cv2.Rodrigues(rvec)

    camera_space_transform = np.eye(4)
    camera_space_transform[:3, :3] = rotation_matrix
    camera_space_transform[:3, 3] = tvec.flatten()

    global_camera_transform = np.linalg.inv(camera_space_transform)

    global_rotation_matrix = global_camera_transform[:3, :3]
    global_rvec, _ = cv2.Rodrigues(global_rotation_matrix)
    print(f"Global transform rotation vector (axis-angle):\n{global_rvec}")

    camera_position = global_camera_transform[:3, 3].copy()

    if success:
        print(f"Camera global position: {camera_position}")
    else:
        print("Failed to solve PnP")


# 5.80706 2.78808 0.510398


if __name__ == "__main__":
    main()
