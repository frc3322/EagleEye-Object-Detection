import os
import cv2
import numpy as np
import json
from pupil_apriltags import Detector
from typing import Tuple

def load_camera_parameters(json_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Load camera matrix and distortion coefficients from a JSON file."""
    with open(json_path, "r") as file:
        data = json.load(file)
    camera_matrix = np.array(data["camera_matrix"], dtype=np.float64)
    distortion_coefficients = np.array(data["distortion_coefficients"], dtype=np.float64)
    return camera_matrix, distortion_coefficients

def draw_axes(
    image: np.ndarray,
    camera_matrix: np.ndarray,
    distortion_coefficients: np.ndarray,
    rvec: np.ndarray,
    tvec: np.ndarray,
    axis_length: float = 0.05,
) -> np.ndarray:
    """Draw 3D axes on the image for the given pose."""
    axis = np.float32(
        [
            [0, 0, 0],
            [axis_length, 0, 0],
            [0, axis_length, 0],
            [0, 0, -axis_length],
        ]
    )
    imgpts, _ = cv2.projectPoints(axis, rvec, tvec, camera_matrix, distortion_coefficients)
    imgpts = np.int32(imgpts).reshape(-1, 2)
    image = cv2.line(image, tuple(imgpts[0]), tuple(imgpts[1]), (0, 0, 255), 3)
    image = cv2.line(image, tuple(imgpts[0]), tuple(imgpts[2]), (0, 255, 0), 3)
    image = cv2.line(image, tuple(imgpts[0]), tuple(imgpts[3]), (255, 0, 0), 3)
    return image

def main() -> None:
    camera_json_path = os.path.join(os.path.dirname(__file__), "camera_intrinsics.json")
    test_image_path = os.path.join(os.path.dirname(__file__), "apriltag_test.png")
    tag_size_meters = 0.1651
    camera_matrix, distortion_coefficients = load_camera_parameters(camera_json_path)
    image = cv2.imread(test_image_path)
    if image is None:
        raise RuntimeError(f"Could not load image: {test_image_path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detector = Detector(families="tag36h11")
    tags = detector.detect(gray)
    for tag in tags:
        object_points = np.array(
            [
                [-tag_size_meters / 2, tag_size_meters / 2, 0],
                [tag_size_meters / 2, tag_size_meters / 2, 0],
                [tag_size_meters / 2, -tag_size_meters / 2, 0],
                [-tag_size_meters / 2, -tag_size_meters / 2, 0],
            ],
            dtype=np.float32,
        )
        image_points = tag.corners.astype(np.float32)
        success, rvec, tvec = cv2.solvePnP(
            object_points, image_points, camera_matrix, distortion_coefficients
        )
        if success:
            x, y, z = tvec.ravel()
            print(f"Tag {tag.tag_id} position (x=forward, y=left, z=up) in meters: ({z}, {-x}, {-y})")
            tag_position = np.array([z, -x, -y])
            image = draw_axes(image, camera_matrix, distortion_coefficients, rvec, tvec, axis_length=tag_size_meters / 2)
            cv2.polylines(
                image, [np.int32(image_points)], isClosed=True, color=(0, 255, 255), thickness=2
            )
            center = tuple(np.int32(tag.center))
            cv2.circle(image, center, 5, (0, 0, 255), -1)
            cv2.putText(
                image,
                f"ID: {tag.tag_id}",
                (center[0] + 10, center[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2,
            )
    #cv2.imshow("AprilTag Pose Test", image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 