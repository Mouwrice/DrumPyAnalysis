from dataclasses import dataclass, asdict


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

    # Path prefix, used to save the measurements in a specific location with a prefix
    output_prefxix: str
    plot_prefix: str
    base_label: str
    diff_label: str

    # Unit conversion factor, 1000 to go from m -> mm
    unit_conversion: float = 1000

    # Offset of the comparison recording, per axis
    axis_offset: (float, float, float) = (0, 0, 0)

    # Whether diff axis should be flipped or not, per axis, e.g. x -> -x
    flip_axis_diff: (bool, bool, bool) = (True, False, True)

    # Scale of the comparison recording, stretched or compressed around the center of the values
    axis_scale: (float, float, float) = None

    # Rotation of the comparison recording
    axis_rotation: float = 0
    # axis reordering, if true: x -> y, y -> z, z -> x
    axis_reorder: bool = True

    # Frame offset, used to align the two recordings
    # The recording that was started first should have an offset, the second recording should then have an offset of 0
    base_frame_offset: int | None = 0
    diff_frame_offset: int | None = None

    def to_string(self):
        return "\n".join([f"{k}: {str(v)}" for k, v in asdict(self).items()])
