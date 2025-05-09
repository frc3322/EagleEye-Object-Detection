import json
from typing import Any, Dict
import numpy as np
import cv2


class Apriltag:
    """Represents an Apriltag with all necessary data from the fmap file."""

    def __init__(
        self,
        tag_id: int,
        family: str,
        size: float,
        transform: list[float],
        unique: bool,
    ) -> None:
        """Initialize an Apriltag object.

        Args:
            tag_id (int): The ID of the Apriltag.
            family (str): The family of the Apriltag.
            size (float): The size of the Apriltag.
            transform (list[float]): The transformation matrix as a flat list.
            unique (bool): Whether the tag is unique.
        """
        self.tag_id = tag_id
        self.family = family
        self.size = size
        self.transform = transform
        self.unique = unique
        
    

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Apriltag object to a dictionary."""
        return {
            "id": self.tag_id,
            "family": self.family,
            "size": self.size,
            "transform": self.transform,
            "unique": self.unique,
        }

    def get_global_transform_matrix(self) -> np.ndarray:
        """Get the 4x4 global transform matrix for this Apriltag."""
        return np.array(self.transform, dtype=np.float64).reshape((4, 4))

    def camera_global_position_from_vectors(
        self, rotation_vector: np.ndarray, translation_vector: np.ndarray
    ) -> np.ndarray:
        """Compute the camera's global position given camera-to-tag rotation and translation vectors.

        Args:
            rotation_vector (np.ndarray): Rotation vector (Rodrigues, shape (3, 1) or (1, 3)).
            translation_vector (np.ndarray): Translation vector (shape (3, 1) or (1, 3)).

        Returns:
            np.ndarray: 3D position of the camera in the global frame (x, y, z).
        """
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        camera_to_tag_transform = np.eye(4, dtype=np.float64)
        camera_to_tag_transform[:3, :3] = rotation_matrix
        camera_to_tag_transform[:3, 3] = translation_vector.flatten()
        tag_to_camera_transform = np.linalg.inv(camera_to_tag_transform)
        tag_global_transform = self.get_global_transform_matrix()
        camera_global_transform = tag_global_transform @ tag_to_camera_transform
        camera_global_position = camera_global_transform[:3, 3]
        return camera_global_position


def load_fmap_file(fmap_file_path: str) -> Dict[int, Apriltag]:
    """Load and parse an fmap apriltag map file into Apriltag objects keyed by id.

    Args:
        fmap_file_path (str): Path to the fmap file.

    Returns:
        Dict[int, Apriltag]: Dictionary of Apriltag objects keyed by their id.
    """
    with open(fmap_file_path, "r", encoding="utf-8") as fmap_file:
        fmap_content = fmap_file.read()
    fmap_data = json.loads(fmap_content)
    apriltag_dict: Dict[int, Apriltag] = {}
    for fiducial in fmap_data.get("fiducials", []):
        tag_id = fiducial["id"]
        family = fiducial["family"]
        size = fiducial["size"]
        transform = fiducial["transform"]
        unique = fiducial["unique"]
        apriltag = Apriltag(
            tag_id=tag_id,
            family=family,
            size=size,
            transform=transform,
            unique=unique,
        )
        apriltag_dict[tag_id] = apriltag
    return apriltag_dict 
