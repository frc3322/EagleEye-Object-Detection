import json
from typing import Any


def offset_fmap_tag_positions(
    input_fmap_path: str, output_fmap_path: str, x_offset: float, y_offset: float, z_offset: float
) -> None:
    """Offset the positions of Apriltags in an fmap file and save the result.

    Args:
        input_fmap_path (str): Path to the input fmap file.
        output_fmap_path (str): Path to the output fmap file.
        x_offset (float): Offset to apply to the x position.
        y_offset (float): Offset to apply to the y position.
        z_offset (float): Offset to apply to the z position.
    """
    with open(input_fmap_path, "r", encoding="utf-8") as infile:
        fmap_data: dict[str, Any] = json.load(infile)

    for fiducial in fmap_data.get("fiducials", []):
        transform = fiducial["transform"]
        if len(transform) == 16:
            transform[3] += x_offset
            transform[7] += y_offset
            transform[11] += z_offset
        else:
            raise ValueError(f"Transform for tag id {fiducial['id']} is not a 4x4 matrix.")

    with open(output_fmap_path, "w", encoding="utf-8") as outfile:
        json.dump(fmap_data, outfile, indent=2)


def main() -> None:
    """Offset the positions of Apriltags in an fmap file and save the result."""
    input_path = "src/apriltags/utils/frc2025r2.json"
    output_path = "src/apriltags/utils/frc2025r2_offset.json"

    offset_fmap_tag_positions(
        input_fmap_path=input_path,
        output_fmap_path=output_path,
        x_offset=-8.774125,
        y_offset=4.025901,
        z_offset=0.0,
    )


if __name__ == "__main__":
    main() 