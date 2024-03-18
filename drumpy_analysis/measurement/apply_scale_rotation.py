from measurement.deviation import remove_average_offset
from measurement.find_optimal_rotation import (
    apply_base_rotation,
)
from measurement.find_optimal_stretch import apply_diff_stretch

from measurement.frame import Frame
from measurement.measurement import Measurement


def apply_scale_rotation(
    base_data: list[Frame], diff_data: list[Frame], measurement: Measurement
):
    """
    Apply the scale to the diff data and the rotation to the base data.
    """
    apply_base_rotation(base_data, diff_data, measurement)
    remove_average_offset(base_data, diff_data, measurement.mapping)
    apply_diff_stretch(base_data, diff_data, measurement)
    remove_average_offset(base_data, diff_data, measurement.mapping)
