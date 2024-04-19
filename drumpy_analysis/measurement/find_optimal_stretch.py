import math
from typing import Self

from drumpy_analysis.measurement.deviation import compute_average_deviation
from drumpy_analysis.measurement.frame import Frame
from drumpy_analysis.measurement.measurement import Measurement


class DeviationFunction:
    """
    A helper class to calculate the deviation for a given scale
    """

    def __init__(
        self: Self,
        base_data: list[Frame],
        diff_data: list[Frame],
        measurement: Measurement,
    ) -> None:
        self.base_data = base_data
        self.diff_data = diff_data
        self.measurement = measurement

    def calculate(self: Self, stretch: list[float]) -> tuple[float, float, float]:
        """
        Calculate the deviation for the given scale
        """
        dev = compute_average_deviation(
            self.base_data,
            self.diff_data,
            self.measurement.markers,
            self.measurement.dominant_fps,
            base_rotation=self.measurement.base_axis_rotation,
            diff_axis_stretch=(stretch[0], stretch[1], stretch[2]),
            diff_axis_centers=self.measurement.base_centers,
            threshold=0,
        )
        return dev.deviation_x, dev.deviation_y, dev.deviation_z


def find_optimal_diff_scale(
    base_data: list[Frame],
    diff_data: list[Frame],
    measurement: Measurement,
) -> tuple[float, float, float]:
    """
    Find the optimal scale for the diff (x, y, z) compared to the base.
    Assumes the deviation has a minimum at the optimal scale.
    Uses Golden-section search to find the optimal scale for each axis. But using the squared deviation instead of the
    deviation itself.
    :return: The optimal scale found
    """
    deviator = DeviationFunction(base_data, diff_data, measurement)

    # The golden ratio gets used to find points to check in Golden-section search
    golden_ration = (math.sqrt(5) + 1) / 2

    print("\n --- Finding optimal stretch for diff data ---\n")

    # The minimum and maximum scale
    left_bound: list[float] = [0.5, 0, 0]
    right_bound: list[float] = [0.5, 10, 10]

    print(f"Stretch left_bound: {left_bound}")
    print(f"Stretch right_bound: {right_bound}")

    dev = deviator.calculate(left_bound)
    left_bound_deviation = [dev[0], dev[1], dev[2]]
    dev = deviator.calculate(right_bound)
    right_bound_deviation = [dev[0], dev[1], dev[2]]

    print(f"Deviation left_bound: {left_bound_deviation}")
    print(f"Deviation right_bound: {right_bound_deviation}")

    eps = 0.01

    iteration = 0
    # Stop when the interval is small enough
    while (
        right_bound[0] - left_bound[0] > eps
        or right_bound[1] - left_bound[1] > eps
        or right_bound[2] - left_bound[2] > eps
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
) -> None:
    """
    Apply the optimal scale to the diff data
    """

    if measurement.diff_axis_stretch is None:
        measurement.diff_axis_stretch = find_optimal_diff_scale(
            base_data, diff_data, measurement
        )

    scale = measurement.diff_axis_stretch
    for frame in diff_data:
        for marker_enum in measurement.markers:
            row = frame.markers[marker_enum]
            x_center = measurement.base_centers[marker_enum][0]
            y_center = measurement.base_centers[marker_enum][1]
            z_center = measurement.base_centers[marker_enum][2]
            row.x = (row.x - x_center) * scale[0] + x_center
            row.y = (row.y - y_center) * scale[1] + y_center
            row.z = (row.z - z_center) * scale[2] + z_center
