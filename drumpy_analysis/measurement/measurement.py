from dataclasses import dataclass, asdict
from typing import TextIO


@dataclass
class Measurement:
    """
    Class to describe a measurement of a tracked recording with another recording
    Defaults are set to be used when comparing qtm with mediapipe
    """

    # The file path of the base recording
    base_recording: str
    # The file path of the comparison recording
    diff_recording: str

    # Marker mapping, used to map the markers from the base recording to the comparison recording
    mapping: dict[int, int]

    # Path prefix, used to save the measurements in a specific location with a prefix, such as a folder
    output_prefxix: str
    plot_prefix: str

    # Per marker, the centrum value of the base recording
    base_centers: dict[int, tuple[float, float, float]] = None

    # Per marker, the centrum value of the comparison recording
    diff_centers: dict[int, tuple[float, float, float]] = None

    # Rotation of the base recording, set to None to find the optimal rotation
    base_axis_rotation: float = None

    # Unit conversion factor, 1000 to go from m -> mm
    unit_conversion: float = 1000

    # axis reordering, if true: x -> y, y -> z, z -> x
    diff_axis_reorder: bool = True

    # Offset of the comparison recording, per axis
    diff_axis_offset: (float, float, float) = (0, 0, 0)

    # Whether diff axis should be flipped or not, per axis, e.g. x -> -x
    diff_flip_axis: (bool, bool, bool) = (True, False, True)

    # Scale of the comparison recording, stretched or compressed around the center of the values
    diff_axis_stretch: tuple[float, float, float] = None

    # Frame offset, used to align the two recordings
    # The recording that was started first should have an offset, the second recording should then have an offset of 0
    base_frame_offset: int | None = 0
    diff_frame_offset: int | None = None

    # Which frame rate should be used, base or diff (0 or 1)
    dominant_fps: int = 1

    # The label of the base and diff recording
    base_label: str = "Qualisys"
    diff_label: str = "Mediapipe"

    def to_string(self):
        return "\n".join([f"{k}: {str(v)}" for k, v in asdict(self).items()])

    def write(self, file: TextIO):
        file.write(self.to_string())
