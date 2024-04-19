import math
from typing import Self

from scipy.spatial.transform import Rotation

from drumpy_analysis.measurement.deviation import compute_average_deviation
from drumpy_analysis.measurement.frame import Frame
from drumpy_analysis.measurement.measurement import Measurement


class DeviationFunction:
    """
    A helper class to calculate the deviation for a given rotation
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

    def calculate(self: Self, rotation: float) -> tuple[float, float]:
        """
        Calculate the deviation for the given rotation.
        We are only interested in the x and y-axis deviation.
        """
        dev = compute_average_deviation(
            self.base_data,
            self.diff_data,
            self.measurement.markers,
            base_rotation=rotation,
            diff_axis_stretch=self.measurement.diff_axis_stretch,
            dominant_fps=1,
        )
        return dev.deviation_x, dev.deviation_y


def find_optimal_base_rotation(
    base_data: list[Frame],
    diff_data: list[Frame],
    measurement: Measurement,
) -> float:
    """
    Find the optimal rotation for the base data to align with the diff data.
    Uses the average absolute deviation to find the optimal rotation.
    Assumes the deviation is a local minimum around the optimal rotation.
    Uses Golden-section search.
    :return: The optimal rotation found
    """
    deviator = DeviationFunction(base_data, diff_data, measurement)

    # The golden ratio gets used to find points to check in Golden-section search
    golden_ration = (math.sqrt(5) + 1) / 2

    print("\n --- Finding optimal base rotation ---\n")

    # The minimum and maximum rotation
    left_bound = -180
    right_bound = 180

    print(f"Rotation left_bound: {left_bound}")
    print(f"Rotation right_bound: {right_bound}")

    # We know that the z-axis remains the same, so we only need to optimize the x and y-axis
    dev = deviator.calculate(left_bound)
    left_deviation = [dev[0], dev[1]]
    dev = deviator.calculate(right_bound)
    right_deviation = [dev[0], dev[1]]

    print(f"Deviation left_bound: {left_deviation}")
    print(f"Deviation right_bound: {right_deviation}")

    eps = 0.1

    iteration = 0
    # Stop when the interval is small enough
    while right_bound - left_bound > eps:
        iteration += 1
        print(f"\nOptimizing rotation, iteration {iteration}:\n")

        new_left_bound = right_bound - (right_bound - left_bound) / golden_ration
        dev = deviator.calculate(new_left_bound)
        new_left_deviation = [dev[0], dev[1]]

        new_right_bound = left_bound + (right_bound - left_bound) / golden_ration
        dev = deviator.calculate(new_right_bound)
        new_right_deviation = [dev[0], dev[1]]

        # If we can lower the deviation for the x or y-axis, we move the bound
        if new_left_deviation[1] < new_right_deviation[1]:
            right_bound = new_right_bound
            right_deviation = new_right_deviation
        else:
            left_bound = new_left_bound
            left_deviation = new_left_deviation

        print(f"New left_bound: {left_bound}")
        print(f"New right_bound: {right_bound}")
        print(f"New deviation left_bound: {left_deviation}")
        print(f"New deviation right_bound: {right_deviation}\n")

    middle = (left_bound + right_bound) / 2
    dev = deviator.calculate(middle)
    print(f"Optimal base rotation: {middle}")
    print(f"Minimal deviation: {dev}")

    return middle


def apply_base_rotation(
    base_data: list[Frame], diff_data: list[Frame], measurement: Measurement
) -> None:
    """
    Apply the rotation to the base data
    """
    if measurement.base_axis_rotation is None:
        measurement.base_axis_rotation = find_optimal_base_rotation(
            base_data, diff_data, measurement
        )

    rotation = Rotation.from_euler("z", measurement.base_axis_rotation, degrees=True)
    for frame in base_data:
        for key in measurement.markers:
            row = frame.markers[key]
            row.x, row.y, row.z = rotation.apply([row.x, row.y, row.z])
