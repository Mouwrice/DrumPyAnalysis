from drumpy_analysis.measurement.deviation import remove_average_offset
from drumpy_analysis.measurement.find_optimal_rotation import (
    apply_base_rotation,
)
from drumpy_analysis.measurement.find_optimal_stretch import apply_diff_stretch

from drumpy_analysis.measurement.frame import Frame
from drumpy_analysis.measurement.measurement import Measurement


def apply_scale_rotation(
    base_data: list[Frame], diff_data: list[Frame], measurement: Measurement
) -> None:
    """
    Apply the scale to the diff data and the rotation to the base data.
    """
    apply_base_rotation(base_data, diff_data, measurement)
    remove_average_offset(base_data, diff_data, measurement.markers, dominant_fps=1)
    apply_diff_stretch(base_data, diff_data, measurement)
    remove_average_offset(base_data, diff_data, measurement.markers, dominant_fps=1)
