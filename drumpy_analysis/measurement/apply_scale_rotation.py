from measurement.find_optimal_rotation import (
    apply_base_rotation,
    find_optimal_base_rotation,
)
from measurement.find_optimal_scale import apply_diff_stretch, find_optimal_diff_scale
from measurement.frame import Frame, get_marker_centers
from measurement.measurement import Measurement


def apply_scale_rotation(
    base_data: list[Frame], diff_data: list[Frame], measurement: Measurement
):
    """
    Apply the scale to the diff data and the rotation to the base data.
    """
    # Both the rotation and scale are known, so we can apply them directly
    if (
        measurement.base_axis_rotation is not None
        or measurement.diff_axis_stretch is not None
    ):
        apply_base_rotation(base_data, diff_data, measurement)
        apply_diff_stretch(base_data, diff_data, measurement)
        return

    # If only the rotation is known, we apply it to the base data
    if measurement.base_axis_rotation is not None:
        apply_base_rotation(base_data, diff_data, measurement)
        # Find the optimal scale for the diff data
        apply_diff_stretch(base_data, diff_data, measurement)
        return

    # If only the scale is known, we apply it to the diff data
    if measurement.diff_axis_stretch is not None:
        apply_diff_stretch(base_data, diff_data, measurement)
        # Find the optimal rotation for the base data
        apply_base_rotation(base_data, diff_data, measurement)
        return

    # If both are none, we iteratively find the optimal rotation and scale
    if measurement.base_axis_rotation is None and measurement.diff_axis_stretch is None:
        measurement.base_axis_rotation = find_optimal_base_rotation(
            base_data, diff_data, measurement
        )

        scale_centers_diff = get_marker_centers(diff_data, measurement.mapping)
        measurement.diff_axis_stretch = find_optimal_diff_scale(
            base_data, diff_data, scale_centers_diff, measurement
        )

        measurement.base_axis_rotation = find_optimal_base_rotation(
            base_data, diff_data, measurement
        )

        apply_base_rotation(base_data, diff_data, measurement)
        apply_diff_stretch(base_data, diff_data, measurement)
