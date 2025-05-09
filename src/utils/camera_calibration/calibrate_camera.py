import cv2
import numpy as np
from typing import Tuple, List, Optional

def get_object_points(
    chessboard_rows: int, chessboard_cols: int, square_size: float
) -> np.ndarray:
    """Generate object points for a chessboard calibration pattern.

    Args:
        chessboard_rows (int): Number of inner rows in the chessboard pattern.
        chessboard_cols (int): Number of inner columns in the chessboard pattern.
        square_size (float): Size of a square in the chessboard pattern (in meters).

    Returns:
        np.ndarray: Array of object points in 3D space.
    """
    object_points = np.zeros((chessboard_rows * chessboard_cols, 3), np.float32)
    object_points[:, :2] = np.mgrid[0:chessboard_cols, 0:chessboard_rows].T.reshape(-1, 2)
    object_points *= square_size
    return object_points

def collect_calibration_points_from_image_array(
    image_array_list: List[np.ndarray],
    chessboard_size: Tuple[int, int],
    square_size: float,
    debug_display: bool = False,
) -> Tuple[List[np.ndarray], List[np.ndarray], Optional[Tuple[int, int]]]:
    """Collect object points and image points from a list of images for camera calibration.

    Args:
        image_array_list (List[np.ndarray]): List of images as numpy arrays.
        chessboard_size (Tuple[int, int]): (rows, cols) of the chessboard pattern (inner corners).
        square_size (float): Size of a square in the chessboard pattern (in meters).
        debug_display (bool, optional): Whether to display debug windows. Defaults to False.

    Returns:
        Tuple[List[np.ndarray], List[np.ndarray], Optional[Tuple[int, int]]]:
            List of object points, list of image points, and image size (width, height) if found.
    """
    object_points_list: List[np.ndarray] = []
    image_points_list: List[np.ndarray] = []
    object_points_template = get_object_points(
        chessboard_size[0], chessboard_size[1], square_size
    )
    image_size: Optional[Tuple[int, int]] = None
    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        30,
        0.001,
    )
    for image in image_array_list:
        if image is None:
            continue
        gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(
            gray_frame, (chessboard_size[1], chessboard_size[0]), None
        )
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
        if debug_display:
            display_frame = image.copy()
            if found:
                cv2.drawChessboardCorners(
                    display_frame,
                    (chessboard_size[1], chessboard_size[0]),
                    refined_corners,
                    found,
                )
            display_frame_resized = cv2.resize(
                display_frame,
                (display_frame.shape[1] // 2, display_frame.shape[0] // 2),
            )
            cv2.imshow("Calibration Debug View", display_frame_resized)
            if cv2.waitKey(30) & 0xFF == 27:
                break
    if debug_display:
        cv2.destroyAllWindows()
    return object_points_list, image_points_list, image_size

def calibrate_camera(
    object_points_list: List[np.ndarray],
    image_points_list: List[np.ndarray],
    image_size: Tuple[int, int],
) -> Tuple[np.ndarray, float]:
    """Calibrate the camera using collected object and image points.

    Args:
        object_points_list (List[np.ndarray]): List of object points in 3D space.
        image_points_list (List[np.ndarray]): List of corresponding image points in 2D.
        image_size (Tuple[int, int]): Size of the calibration images (width, height).

    Returns:
        Tuple[np.ndarray, float]: Camera matrix and mean reprojection error.
    """
    _, camera_matrix, distortion_coefficients, rotation_vectors, translation_vectors = cv2.calibrateCamera(
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
    return camera_matrix, mean_reprojection_error

def compute_mean_reprojection_error(
    object_points_list: List[np.ndarray],
    image_points_list: List[np.ndarray],
    rotation_vectors: List[np.ndarray],
    translation_vectors: List[np.ndarray],
    camera_matrix: np.ndarray,
    distortion_coefficients: np.ndarray,
) -> float:
    """Compute the mean reprojection error for the calibration.

    Args:
        object_points_list (List[np.ndarray]): List of object points in 3D space.
        image_points_list (List[np.ndarray]): List of corresponding image points in 2D.
        rotation_vectors (List[np.ndarray]): List of rotation vectors from calibration.
        translation_vectors (List[np.ndarray]): List of translation vectors from calibration.
        camera_matrix (np.ndarray): Camera matrix from calibration.
        distortion_coefficients (np.ndarray): Distortion coefficients from calibration.

    Returns:
        float: Mean reprojection error.
    """
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

def calibrate_camera_from_image_array(
    image_array_list: List[np.ndarray],
    chessboard_rows: int,
    chessboard_cols: int,
    square_size: float,
    minimum_patterns: int = 5,
    debug_display: bool = False,
) -> Optional[Tuple[np.ndarray, float]]:
    """Perform camera calibration from a list of images (numpy arrays).

    Args:
        image_array_list (List[np.ndarray]): List of images as numpy arrays.
        chessboard_rows (int): Number of inner rows in the chessboard pattern.
        chessboard_cols (int): Number of inner columns in the chessboard pattern.
        square_size (float): Size of a square in the chessboard pattern (in meters).
        minimum_patterns (int, optional): Minimum number of valid patterns required. Defaults to 5.
        debug_display (bool, optional): Whether to display debug windows. Defaults to False.

    Returns:
        Optional[Tuple[np.ndarray, float]]: Camera matrix and mean reprojection error, or None if not enough valid patterns are found.
    """
    chessboard_size = (chessboard_rows, chessboard_cols)
    object_points_list, image_points_list, image_size = collect_calibration_points_from_image_array(
        image_array_list,
        chessboard_size,
        square_size,
        debug_display,
    )
    if object_points_list is None or len(object_points_list) < minimum_patterns:
        return None
    if image_size is None:
        return None
    camera_matrix, mean_reprojection_error = calibrate_camera(
        object_points_list, image_points_list, image_size
    )
    return camera_matrix, mean_reprojection_error

def undistort_image(
    image: np.ndarray,
    camera_matrix: np.ndarray,
    distortion_coefficients: np.ndarray,
) -> np.ndarray:
    """Undistort an image using the provided camera matrix and distortion coefficients.

    Args:
        image (np.ndarray): Input distorted image.
        camera_matrix (np.ndarray): Camera matrix from calibration.
        distortion_coefficients (np.ndarray): Distortion coefficients from calibration.

    Returns:
        np.ndarray: Undistorted image.
    """
    height, width = image.shape[:2]
    new_camera_matrix, region_of_interest = cv2.getOptimalNewCameraMatrix(
        camera_matrix, distortion_coefficients, (width, height), 1, (width, height)
    )
    undistorted_image = cv2.undistort(image, camera_matrix, distortion_coefficients, None, new_camera_matrix)
    x, y, w, h = region_of_interest
    undistorted_cropped = undistorted_image[y : y + h, x : x + w]
    return undistorted_cropped
