import csv
from typing import Self

from drumpy_analysis.measurement.marker import Marker, parse_row


class Frame:
    """
    A frame consistens of multiple Markers, each Marker is a marker postition at a certain frame
    """

    def __init__(self: Self, rows: list[Marker], time_ms: float, frame: int) -> None:
        self.rows: list[Marker] = rows
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
            frame = Frame([row], row.time, row.frame)
            for line in reader:
                row = parse_row(line, scale=scale)
                if row.frame == frame.frame:
                    frame.rows.append(row)
                else:
                    frames.append(frame)
                    frame = Frame([row], row.time, row.frame)
        return frames


def get_marker_centers(
    frames: list[Frame], mapping: dict[int, int]
) -> dict[int, tuple[float, float, float]]:
    """
    Get the average value for each marker
    """
    marker_centers = {}
    for frame in frames:
        for marker in mapping.values():
            if marker not in marker_centers:
                marker_centers[marker] = (0, 0, 0)
            row = frame.rows[marker]
            marker_centers[marker] = (
                marker_centers[marker][0] + (row.x / len(frames)),
                marker_centers[marker][1] + (row.y / len(frames)),
                marker_centers[marker][2] + (row.z / len(frames)),
            )
    return marker_centers


def extract_rows(frames: list[Frame], marker_index: int) -> list[Marker]:
    """
    Extract the rows for a certain marker
    """
    return [frame.rows[marker_index] for frame in frames]
