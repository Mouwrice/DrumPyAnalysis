import csv
from typing import Self

from drumpy.mediapipe_pose.mediapipe_markers import MarkerEnum  # type: ignore

from drumpy_analysis.measurement.frame import Frame
from drumpy_analysis.measurement.marker import Marker


class QTMFrame:
    """
    Class that represents a frame in a QTM measurement.
    """

    def __init__(
        self: Self,
        time_ms: float,
        frame: int,
        marker_positions: dict[MarkerEnum, tuple[float, float, float]],
    ) -> None:
        self.time_ms: float = time_ms
        self.frame: int = frame
        self.marker_positions: dict[
            MarkerEnum, tuple[float, float, float]
        ] = marker_positions

    def __str__(self: Self) -> str:
        return f"Frame {self.frame} at {self.time_ms} ms: {self.marker_positions}"

    def to_frame(self: Self) -> Frame:
        """
        Convert the QTMFrame to a Frame object
        """
        rows: list[Marker] = []
        for marker, position in self.marker_positions.items():
            rows.append(
                Marker(
                    self.frame,
                    self.time_ms,
                    marker.value,
                    position[0],
                    position[1],
                    position[2],
                    None,
                    None,
                    0,
                )
            )

        return Frame(rows, self.time_ms, self.frame)

    @staticmethod
    def from_tsv_row(
        row: list[str], marker_names: list[str], time_ms: float, frame: int
    ) -> "QTMFrame":
        """
        Create a Frame object from a row in a TSV file.
        :param row: Row from the TSV file
        :param marker_names: Names of the markers
        :param time_ms: Time in ms
        :param frame: Frame number
        :return: Frame object
        """
        marker_positions: dict[MarkerEnum, tuple[float, float, float]] = {}
        for i, marker_name in enumerate(marker_names):
            marker = MarkerEnum.from_qtm_label(marker_name)
            marker_positions[marker] = (
                float(row[i * 3]),
                float(row[i * 3 + 1]),
                float(row[i * 3 + 2]),
            )
        return QTMFrame(time_ms, frame, marker_positions)

    @staticmethod
    def remove_time_offset(frames: list["QTMFrame"]) -> None:
        """
        Remove the time offset from the frames
        """
        time_offset = frames[0].time_ms
        for frame in frames:
            frame.time_ms -= time_offset


class QTM:
    """
    Class that represents a QTM measurement.
    Reads data from TSV files produced by QTM.
    """

    def __init__(
        self: Self,
        no_of_frames: int,
        frequency: int,
        marker_names: list[str],
        frames: list[QTMFrame],
    ) -> None:
        self.no_of_frames: int = no_of_frames
        self.frequency: int = frequency
        self.marker_names: list[str] = marker_names
        self.frames: list[QTMFrame] = frames

    def __str__(self: Self) -> str:
        return f"QTM measurement with {self.no_of_frames} frames at {self.frequency} Hz"

    @staticmethod
    def from_tsv(path: str) -> "QTM":
        """
        Create a QTM object from a TSV file.
        :param path: Path to the TSV file
        :return: QTM object
        """
        with open(path, "r") as file:
            reader = csv.reader(file, delimiter="\t")
            line_1 = next(reader)
            assert line_1[0] == "NO_OF_FRAMES"
            no_of_frames = int(line_1[1])

            line_2 = next(reader)
            assert line_2[0] == "NO_OF_CAMERAS"

            line_3 = next(reader)
            assert line_3[0] == "NO_OF_MARKERS"
            no_of_markers = int(line_3[1])

            line_4 = next(reader)
            assert line_4[0] == "FREQUENCY"
            frequency = int(line_4[1])

            line_5 = next(reader)
            assert line_5[0] == "NO_OF_ANALOG"

            line_6 = next(reader)
            assert line_6[0] == "ANALOG_FREQUENCY"

            line_7 = next(reader)
            assert line_7[0] == "DESCRIPTION"

            line_8 = next(reader)
            assert line_8[0] == "TIME_STAMP"

            line_9 = next(reader)
            assert line_9[0] == "DATA_INCLUDED"
            assert line_9[1] == "3D"

            line_10 = next(reader)
            assert line_10[0] == "MARKER_NAMES"
            marker_names = line_10[1:]
            assert len(marker_names) == no_of_markers

            line_11 = next(reader)
            assert line_11[0] == "TRAJECTORY_TYPES"

            time_delta = 1000 / frequency
            frames: list[QTMFrame] = []
            for i, row in enumerate(reader):
                assert len(row) == no_of_markers * 3
                frames.append(
                    QTMFrame.from_tsv_row(row, marker_names, i * time_delta, i)
                )

        return QTM(no_of_frames, frequency, marker_names, frames)


if __name__ == "__main__":
    qtm = QTM.from_tsv("data/Qualisys/Data/maurice_drum_fast.tsv")
    print(qtm)
