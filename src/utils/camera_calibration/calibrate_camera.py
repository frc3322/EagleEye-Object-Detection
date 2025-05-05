import os
import glob
import cv2
import numpy as np
import json
from typing import Tuple, List

calibration_images_folder = os.path.join(os.path.dirname(__file__), "calibration_images")
chessboard_inner_rows: int = 10
chessboard_inner_cols: int = 7
chessboard_square_size_meters: float = 0.025
calibration_output_path: str = os.path.join(os.path.dirname(__file__), "camera_intrinsics.json")
debug_display_enabled: bool = True
minimum_patterns: int = 5


def get_object_points(
    rows: int, cols: int, square_size: float
) -> np.ndarray:
    object_points = np.zeros((rows * cols, 3), np.float32)
    object_points[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
    object_points *= square_size
    return object_points


def collect_calibration_points_from_images(
    images_folder: str,
    chessboard_size: Tuple[int, int],
    square_size: float,
    min_patterns: int,
    debug_display: bool = False,
) -> Tuple[List[np.ndarray], List[np.ndarray], Tuple[int, int]]:
    object_points_list: List[np.ndarray] = []
    image_points_list: List[np.ndarray] = []
    object_points_template = get_object_points(
        chessboard_size[0], chessboard_size[1], square_size
    )
    image_size: Tuple[int, int] = (0, 0)
    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        30,
        0.001,
    )
    image_paths = glob.glob(os.path.join(images_folder, "*.jpg")) + glob.glob(os.path.join(images_folder, "*.png"))
    for image_path in image_paths:
        image = cv2.imread(image_path)
        if image is None:
            continue
        gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(
            gray_frame, (chessboard_size[1], chessboard_size[0]), None
        )
        display_frame = image.copy()
        if found:
            refined_corners = cv2.cornerSubPix(
                gray_frame,
                corners,
                (11, 11),
                (-1, -1),
                criteria,
            )
            object_points_list.append(object_points_template)
            image_points_list.append(refined_corners)
            image_size = (gray_frame.shape[1], gray_frame.shape[0])
            cv2.drawChessboardCorners(
                display_frame,
                (chessboard_size[1], chessboard_size[0]),
                refined_corners,
                found,
            )
        else:
            print("No corners found")
            if corners is not None:
                cv2.drawChessboardCorners(
                    display_frame,
                    (chessboard_size[1], chessboard_size[0]),
                    corners,
                    found,
                )
        if debug_display:
            display_frame_resized = cv2.resize(
                display_frame,
                (display_frame.shape[1] // 2, display_frame.shape[0] // 2),
            )
            cv2.imshow("Calibration Debug View", display_frame_resized)
            if cv2.waitKey(30) & 0xFF == 27:
                break
    if debug_display:
        cv2.destroyAllWindows()
    print(f"Valid patterns found: {len(object_points_list)}")
    return object_points_list, image_points_list, image_size


def calibrate_camera(
    object_points_list: List[np.ndarray],
    image_points_list: List[np.ndarray],
    image_size: Tuple[int, int],
) -> Tuple[np.ndarray, np.ndarray, List[np.ndarray], List[np.ndarray], float]:
    ret, camera_matrix, distortion_coefficients, rotation_vectors, translation_vectors = cv2.calibrateCamera(
        object_points_list, image_points_list, image_size, None, None
    )
    mean_reprojection_error = compute_mean_reprojection_error(
        object_points_list,
        image_points_list,
        rotation_vectors,
        translation_vectors,
        camera_matrix,
        distortion_coefficients,
    )
    return (
        camera_matrix,
        distortion_coefficients,
        rotation_vectors,
        translation_vectors,
        mean_reprojection_error,
    )


def compute_mean_reprojection_error(
    object_points_list: List[np.ndarray],
    image_points_list: List[np.ndarray],
    rotation_vectors: List[np.ndarray],
    translation_vectors: List[np.ndarray],
    camera_matrix: np.ndarray,
    distortion_coefficients: np.ndarray,
) -> float:
    total_error = 0.0
    for object_points, image_points, rotation_vector, translation_vector in zip(
        object_points_list, image_points_list, rotation_vectors, translation_vectors
    ):
        projected_image_points, _ = cv2.projectPoints(
            object_points, rotation_vector, translation_vector, camera_matrix, distortion_coefficients
        )
        error = np.linalg.norm(image_points - projected_image_points, axis=1).mean()
        total_error += error
    mean_error = total_error / len(object_points_list)
    return mean_error


def undistort_and_save_example(
    camera_matrix: np.ndarray,
    distortion_coefficients: np.ndarray,
    image_size: Tuple[int, int],
    image_path: str,
    output_path: str = "calibresult.png",
) -> None:
    image = cv2.imread(image_path)
    if image is None:
        return
    h, w = image.shape[:2]
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
        camera_matrix, distortion_coefficients, (w, h), 1, (w, h)
    )
    undistorted = cv2.undistort(image, camera_matrix, distortion_coefficients, None, new_camera_matrix)
    x, y, w, h = roi
    undistorted_cropped = undistorted[y : y + h, x : x + w]
    cv2.imwrite(output_path, undistorted_cropped)


def save_calibration_results(
    output_path: str,
    camera_matrix: np.ndarray,
    distortion_coefficients: np.ndarray,
    mean_reprojection_error: float,
    image_size: Tuple[int, int],
) -> None:
    def to_native(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        return obj
    calibration_data = {
        "camera_matrix": to_native(camera_matrix),
        "distortion_coefficients": to_native(distortion_coefficients),
        "mean_reprojection_error": float(mean_reprojection_error),
        "image_width": int(image_size[0]),
        "image_height": int(image_size[1]),
    }
    with open(output_path, "w") as output_file:
        json.dump(calibration_data, output_file, indent=2)


def main() -> None:
    chessboard_size = (chessboard_inner_rows, chessboard_inner_cols)
    object_points_list, image_points_list, image_size = collect_calibration_points_from_images(
        calibration_images_folder,
        chessboard_size,
        chessboard_square_size_meters,
        minimum_patterns,
        debug_display_enabled,
    )
    if len(object_points_list) < minimum_patterns:
        raise RuntimeError("Not enough valid frames with detected chessboard corners for calibration.")
    print(f"Collected {len(object_points_list)} valid patterns")
    print("Calibrating camera...")
    camera_matrix, distortion_coefficients, rotation_vectors, translation_vectors, mean_reprojection_error = calibrate_camera(
        object_points_list, image_points_list, image_size
    )
    print(f"Camera matrix:\n{camera_matrix}")
    print(f"Distortion coefficients:\n{distortion_coefficients}")
    print(f"Mean reprojection error: {mean_reprojection_error}")
    save_calibration_results(
        calibration_output_path,
        camera_matrix,
        distortion_coefficients,
        mean_reprojection_error,
        image_size,
    )
    if len(glob.glob(os.path.join(calibration_images_folder, "*.jpg"))) > 0:
        undistort_and_save_example(
            camera_matrix,
            distortion_coefficients,
            image_size,
            glob.glob(os.path.join(calibration_images_folder, "*.jpg"))[0],
            output_path="calibresult.png",
        )


if __name__ == "__main__":
    main()
