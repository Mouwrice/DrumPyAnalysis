from typing import Self, Union


class Marker:
    """
    Represents a single row of a CSV file
    """

    def __init__(
        self: Self,
        frame: int,
        time: int,
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
        self.time: int = time
        self.index: int = index
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.visibility: float | None = visibility
        self.presence: float | None = presence
        self.landmark_type: int = landmark_type


def parse_row(row: Union[dict, str], scale: float = 1.0) -> Marker:
    frame = int(row["frame"])
    time = int(row["time"])
    index = int(row["index"])
    x = float(row["x"]) * scale
    y = float(row["y"]) * scale
    z = float(row["z"]) * scale
    visibility = row["visibility"]
    presence = row["presence"]
    landmark_type = row.get("landmark_type", 0)

    return Marker(frame, time, index, x, y, z, visibility, presence, landmark_type)
