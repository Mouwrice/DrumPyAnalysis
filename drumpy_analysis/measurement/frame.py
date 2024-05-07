import csv
from typing import Self

from drumpy_analysis.measurement.marker import Marker, parse_row

from drumpy.mediapipe_pose.mediapipe_markers import MarkerEnum


class Frame:
    """
    A frame consistens of multiple Markers, each Marker is a marker postition at a certain frame
    """

    def __init__(
        self: Self, markers: dict[MarkerEnum, Marker], time_ms: float, frame: int
    ) -> None:
        self.markers: dict[MarkerEnum, Marker] = markers
        self.time_ms: float = time_ms
        self.frame: int = frame

    @staticmethod
    def frames_from_csv(csv_file: str, scale: float = 1.0) -> list["Frame"]:
        """
        Read a CSV file and return a list of frames
        """
        frames: list[Frame] = []
        with open(csv_file, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            row = parse_row(next(reader))
            frame = Frame({row.marker_enum: row}, row.time, row.frame)
            for line in reader:
                row = parse_row(line, scale=scale)
                if row.frame == frame.frame:
                    frame.markers[row.marker_enum] = row
                else:
                    frames.append(frame)
                    frame = Frame({row.marker_enum: row}, row.time, row.frame)
        return frames


def get_marker_centers(
    frames: list[Frame], markers: list[MarkerEnum]
) -> dict[int, tuple[float, float, float]]:
    """
    Get the average value for each marker
    """
    marker_centers = {}
    for frame in frames:
        for marker_enum in markers:
            if marker_enum not in marker_centers:
                marker_centers[marker_enum] = (0, 0, 0)
            row = frame.markers[marker_enum]
            marker_centers[marker_enum] = (
                marker_centers[marker_enum][0] + (row.x / len(frames)),
                marker_centers[marker_enum][1] + (row.y / len(frames)),
                marker_centers[marker_enum][2] + (row.z / len(frames)),
            )
    return marker_centers


def extract_rows(frames: list[Frame], marker_index: MarkerEnum) -> list[Marker]:
    """
    Extract the rows for a certain marker
    """
    return [frame.markers[marker_index] for frame in frames]
