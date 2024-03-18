import math

from measurement.deviation import average_absolute_deviation
from measurement.frame import Frame, get_marker_centers
from measurement.measurement import Measurement


class DeviationFunction:
    """
    A helper class to calculate the deviation for a given scale
    """

    def __init__(
        self,
        base_data: list[Frame],
        diff_data: list[Frame],
        measurement: Measurement,
        stretch_centers_diff: dict[int, tuple[float, float, float]],
    ):
        self.base_data = base_data
        self.diff_data = diff_data
        self.measurement = measurement
        self.stretch_centers_diff = stretch_centers_diff

    def calculate(self, stretch: list[float]) -> tuple[float, float, float]:
        """
        Calculate the deviation for the given scale
        """
        dev = average_absolute_deviation(
            self.base_data,
            self.diff_data,
            self.measurement.mapping,
            base_rotation=self.measurement.base_axis_rotation,
            stretch_diff=(stretch[0], stretch[1], stretch[2]),
            stretch_centers_diff=self.stretch_centers_diff,
        )
        return dev.x_abs, dev.y_abs, dev.z_abs


def find_optimal_diff_scale(
    base_data: list[Frame],
    diff_data: list[Frame],
    scale_centers_diff: dict[int, tuple[float, float, float]],
    measurement: Measurement,
) -> tuple[float, float, float]:
    """
    Find the optimal scale for the diff (x, y, z) compared to the base.
    Assumes the deviation has a minimum at the optimal scale.
    Uses Golden-section search to find the optimal scale for each axis.
    :return: The optimal scale found
    """
    deviator = DeviationFunction(base_data, diff_data, measurement, scale_centers_diff)

    # The golden ratio gets used to find points to check in Golden-section search
    golden_ration = (math.sqrt(5) + 1) / 2

    print("\n --- Finding optimal stretch for diff data ---\n")

    # The minimum and maximum scale
    left_bound: list[float] = [0, 0, 0]
    right_bound: list[float] = [10, 10, 10]

    print(f"Stretch left_bound: {left_bound}")
    print(f"Stretch right_bound: {right_bound}")

    dev = deviator.calculate(left_bound)
    left_bound_deviation = [dev[0], dev[1], dev[2]]
    dev = deviator.calculate(right_bound)
    right_bound_deviation = [dev[0], dev[1], dev[2]]

    print(f"Deviation left_bound: {left_bound_deviation}")
    print(f"Deviation right_bound: {right_bound_deviation}")

    iteration = 0
    # Stop when the interval is small enough
    while (
        right_bound[0] - left_bound[0] > 0.01
        or right_bound[1] - left_bound[1] > 0.01
        or right_bound[2] - left_bound[2] > 0.01
    ):
        iteration += 1
        print(f"\nOptimizing scale, iteration {iteration}:\n")

        new_left_bound = [
            right_bound[0] - (right_bound[0] - left_bound[0]) / golden_ration,
            right_bound[1] - (right_bound[1] - left_bound[1]) / golden_ration,
            right_bound[2] - (right_bound[2] - left_bound[2]) / golden_ration,
        ]
        dev = deviator.calculate(new_left_bound)
        new_left_bound_deviation = [dev[0], dev[1], dev[2]]

        new_right_bound = [
            left_bound[0] + (right_bound[0] - left_bound[0]) / golden_ration,
            left_bound[1] + (right_bound[1] - left_bound[1]) / golden_ration,
            left_bound[2] + (right_bound[2] - left_bound[2]) / golden_ration,
        ]
        dev = deviator.calculate(new_right_bound)
        new_right_bound_deviation = [dev[0], dev[1], dev[2]]

        # Optimize each axis independently
        for i in range(3):
            if new_left_bound_deviation[i] < new_right_bound_deviation[i]:
                right_bound[i] = new_right_bound[i]
                right_bound_deviation[i] = new_right_bound_deviation[i]

            else:
                left_bound[i] = new_left_bound[i]
                left_bound_deviation[i] = new_left_bound_deviation[i]

        print(f"New left_bound: {left_bound}")
        print(f"New right_bound: {right_bound}")
        print(f"New left_bound_deviation: {left_bound_deviation}")
        print(f"New right_bound_deviation: {right_bound_deviation}\n")

    middle = [(left_bound[i] + right_bound[i]) / 2 for i in range(3)]
    dev = deviator.calculate(middle)
    middle_deviation = [dev[0], dev[1], dev[2]]
    print(f"Optimal diff stretch: {middle}")
    print(f"Minimal deviation: {middle_deviation}")

    return middle[0], middle[1], middle[2]


def apply_diff_stretch(
    base_data: list[Frame],
    diff_data: list[Frame],
    measurement: Measurement,
):
    """
    Apply the optimal scale to the diff data
    """
    scale_centers_diff = get_marker_centers(diff_data, measurement.mapping)

    if measurement.diff_axis_stretch is None:
        measurement.diff_axis_stretch = find_optimal_diff_scale(
            base_data, diff_data, scale_centers_diff, measurement
        )

    scale = measurement.diff_axis_stretch
    for frame in diff_data:
        for key in scale_centers_diff.keys():
            row = frame.rows[key]
            row.x = (row.x - scale_centers_diff[key][0]) * scale[
                0
            ] + scale_centers_diff[key][0]
            row.y = (row.y - scale_centers_diff[key][1]) * scale[
                1
            ] + scale_centers_diff[key][1]
            row.z = (row.z - scale_centers_diff[key][2]) * scale[
                2
            ] + scale_centers_diff[key][2]
