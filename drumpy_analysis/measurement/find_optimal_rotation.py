from scipy.spatial.transform import Rotation

from measurement.deviation import average_absolute_deviation
from measurement.frame import Frame
from measurement.measurement import Measurement


def find_optimal_base_rotation(
    base_data: list[Frame],
    diff_data: list[Frame],
    scale_centers_diff: dict[int, tuple[float, float, float]],
    measurement: Measurement,
) -> float:
    """
    Find the optimal rotation for the base data to align with the diff data.
    Uses the average absolute deviation to find the optimal rotation.
    Assumes the deviation is a local minimum around the optimal rotation.
    :return: The optimal rotation found
    """

    print("\n Finding optimal base rotation\n")

    # The minimum and maximum rotation
    rotation_low = -180
    rotation_middle = 0
    rotation_high = 180

    print(f"Rotation min: {rotation_low}")
    print(f"Rotation max: {rotation_high}")

    dev = average_absolute_deviation(
        base_data,
        diff_data,
        measurement.mapping,
        base_rotation=rotation_low,
        scale_diff=measurement.diff_axis_scale,
        scale_centers_diff=scale_centers_diff,
    )

    # We know that the z-axis remains the same, so we only need to optimize the x and y-axis
    low_deviation = [dev.x_abs, dev.y_abs]
    dev = average_absolute_deviation(
        base_data,
        diff_data,
        measurement.mapping,
        base_rotation=rotation_middle,
        scale_diff=measurement.diff_axis_scale,
        scale_centers_diff=scale_centers_diff,
    )
    middle_deviation = [dev.x_abs, dev.y_abs]

    i = 0
    # The binary search, stop when the deviation difference is smaller than 0.01
    while (
        abs(middle_deviation[0] - low_deviation[0]) > 0.01
        or abs(middle_deviation[1] - low_deviation[1]) > 0.01
    ):
        i += 1
        print(f"Optimizing rotation, iteration {i}")
        print(f"Rotation: {rotation_middle}")
        print(f"Deviation: {middle_deviation}\n")

        # Optimize each axis independently
        if sum(middle_deviation) < sum(low_deviation):
            rotation_low = rotation_middle
            low_deviation = middle_deviation
        else:
            rotation_high = rotation_middle

        rotation_middle = (rotation_low + rotation_high) / 2

        dev = average_absolute_deviation(
            base_data,
            diff_data,
            measurement.mapping,
            base_rotation=rotation_middle,
            scale_diff=measurement.diff_axis_scale,
            scale_centers_diff=scale_centers_diff,
        )
        middle_deviation = (dev.x_abs, dev.y_abs)

    print(f"Optimal rotation: {rotation_middle}")
    return rotation_middle


def apply_base_rotation(
    base_data: list[Frame], diff_data: list[Frame], measurement: Measurement
):
    """
    Apply the rotation to the base data
    """
    if measurement.base_axis_rotation is None:
        measurement.base_axis_rotation = find_optimal_base_rotation(
            base_data, diff_data, measurement.diff_scale_centers, measurement
        )

    rotation = Rotation.from_euler("z", measurement.base_axis_rotation, degrees=True)
    for frame in base_data:
        for key in measurement.mapping.keys():
            row = frame.rows[key]
            row.x, row.y, row.z = rotation.apply([row.x, row.y, row.z])
