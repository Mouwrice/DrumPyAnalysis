from typing import Self


class Marker:
    """
    Represents a single row of a CSV file
    """

    def __init__(
        self: Self,
        frame: int,
        time: float,
        index: int,
        x: float,
        y: float,
        z: float,
        visibility: float | None,
        presence: float | None,
        landmark_type: int,
    ) -> None:
        """Class for storing a row of a CSV file"""
        self.frame: int = frame
        self.time: float = time
        self.index: int = index
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.visibility: float | None = visibility
        self.presence: float | None = presence
        self.landmark_type: int = landmark_type


def parse_row(row: dict[str, any], scale: float = 1.0) -> Marker:
    frame: int = int(row["frame"])
    time: int = int(row["time"])
    index: int = int(row["index"])
    x: float = float(row["x"]) * scale
    y: float = float(row["y"]) * scale
    z: float = float(row["z"]) * scale
    visibility: float = float(row["visibility"])
    presence: float = float(row["presence"])
    landmark_type: int = row.get("landmark_type", 0)

    return Marker(frame, time, index, x, y, z, visibility, presence, landmark_type)
