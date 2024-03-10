from dataclasses import dataclass


@dataclass
class Measurement:
    """
    Class to describe a measurement of a tracked recording with another recording
    """

    # The file path of the base recording
    base_recording: str
    # The file path of the comparison recording
    diff_recording: str
    # Unit conversion factor, 1000 to go from m -> mm
    unit_conversion: float
    base_frame_offset: int
    diff_frame_offset: int

    # Offset of the comparison recording, per axis
    axis_offset: (float, float, float)
    # The scale difference between the two recordings, per axis
    axis_scale: (float, float, float)
    # Rotation of the comparison recording
    axis_rotation: float
    # axis reordering, if true: x -> y, y -> z, z -> x
    axis_reorder: bool

    # Marker mapping, used to map the markers from the base recording to the comparison recording
    mapping: dict[int, int]

    # Path prefix, used to save the measurements in a specific location with a prefix
    output_prefxix: str
    plot_prefix: str
    base_label: str
    diff_label: str
