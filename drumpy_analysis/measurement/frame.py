import csv

from drumpy_analysis.measurement.marker import Marker
from measurement import marker


class Frame:
    """
    A frame consistens of multiple Markers, each Marker is a marker postition at a certain frame
    """

    def __init__(self):
        self.rows: list[Marker] = []
        self.time_ms: int = 0
        self.frame: int = 0


def frames_from_csv(csv_file: str, scale: float = 1.0) -> list[Frame]:
    """
    Read a CSV file and return a list of frames
    """
    frames: list[Frame] = []
    with open(csv_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        row = marker.parse_row(next(reader))
        frame = Frame()
        frame.frame = row.frame
        frame.time_ms = row.time
        frame.rows.append(row)
        for row in reader:
            row = marker.parse_row(row, scale=scale)
            if row.frame == frame.frame:
                frame.rows.append(row)
            else:
                frames.append(frame)
                frame = Frame()
                frame.frame = row.frame
                frame.time_ms = row.time
                frame.rows.append(row)
    return frames


def extract_rows(frames: list[Frame], marker_index: int) -> list[Marker]:
    """
    Extract the rows for a certain marker
    """
    return [frame.rows[marker_index] for frame in frames]
