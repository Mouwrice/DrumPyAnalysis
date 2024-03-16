from measurement.deviation import average_absolute_deviation
from measurement.frame import Frame, get_marker_centers
from measurement.measurement import Measurement


def find_optimal_diff_scale(
    base_data: list[Frame],
    diff_data: list[Frame],
    scale_centers_diff: dict[int, tuple[float, float, float]],
    measurement: Measurement,
):
    """
    Find the optimal scale for the diff (x, y, z) compared to the base.
    Uses the average deviations and binary search to find the optimal scale.
    Assumes the deviation has a minimum at the optimal scale.
    """

    print("\nFinding optimal scale for diff data\n")

    # The minimum and maximum scale
    scale_low = (0, 0, 0)
    scale_middle = (5, 5, 5)
    scale_high = (10, 10, 10)

    print(f"Scale min: {scale_low}")
    print(f"Scale max: {scale_middle}")

    dev = average_absolute_deviation(
        base_data,
        diff_data,
        measurement.mapping,
        scale_diff=scale_low,
        scale_centers_diff=scale_centers_diff,
    )
    low_deviation = [dev.x_abs, dev.y_abs, dev.z_abs]
    dev = average_absolute_deviation(
        base_data,
        diff_data,
        measurement.mapping,
        scale_diff=scale_middle,
        scale_centers_diff=scale_centers_diff,
    )
    middle_deviation = [dev.x_abs, dev.y_abs, dev.z_abs]

    i = 0
    # The binary search, stop when the deviation difference is smaller than 0.01
    while (
        (scale_high[0] - scale_low[0]) > 0.01
        or (scale_high[1] - scale_low[1]) > 0.01
        or (scale_high[2] - scale_low[2]) > 0.01
    ):
        i += 1
        print(f"Optimizing scale, iteration {i}")
        print(f"Scale: {scale_middle}")
        print(f"Deviation: {middle_deviation}\n")
        # Optimize each axis independently
        scale_low = (
            scale_low[0] if middle_deviation[0] > low_deviation[0] else scale_middle[0],
            scale_low[1] if middle_deviation[1] > low_deviation[1] else scale_middle[1],
            scale_low[2] if middle_deviation[2] > low_deviation[2] else scale_middle[2],
        )
        scale_high = (
            scale_high[0]
            if middle_deviation[0] < low_deviation[0]
            else scale_middle[0],
            scale_high[1]
            if middle_deviation[1] < low_deviation[1]
            else scale_middle[1],
            scale_high[2]
            if middle_deviation[2] < low_deviation[2]
            else scale_middle[2],
        )
        scale_middle = (
            (scale_low[0] + scale_high[0]) / 2,
            (scale_low[1] + scale_high[1]) / 2,
            (scale_low[2] + scale_high[2]) / 2,
        )

        dev = average_absolute_deviation(
            base_data,
            diff_data,
            measurement.mapping,
            scale_diff=scale_middle,
            scale_centers_diff=scale_centers_diff,
        )
        middle_deviation = [dev.x_abs, dev.y_abs, dev.z_abs]

    print(f"Optimal scale: {scale_middle}")
    print(f"Deviation: {middle_deviation}")
    return scale_middle


def apply_scale(
    base_data: list[Frame],
    diff_data: list[Frame],
    measurement: Measurement,
):
    """
    Apply the optimal scale to the diff data
    """
    scale_centers_diff = get_marker_centers(diff_data, measurement.mapping)

    if measurement.axis_scale is None:
        measurement.axis_scale = find_optimal_diff_scale(
            base_data, diff_data, scale_centers_diff, measurement
        )

    scale = measurement.axis_scale
    for frame in diff_data:
        for key in scale_centers_diff.keys():
            row = frame.rows[key]
            row.x += (row.x - scale_centers_diff[key][0]) * scale[0]
            row.y += (row.y - scale_centers_diff[key][1]) * scale[1]
            row.z += (row.z - scale_centers_diff[key][2]) * scale[2]
