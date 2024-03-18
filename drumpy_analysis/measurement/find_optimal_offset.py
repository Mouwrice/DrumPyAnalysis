from measurement.deviation import calculate_deviations
from measurement.frame import Frame


def find_optimal_base_offset(
    base_data: list[Frame],
    diff_data: list[Frame],
    max_offset: int = 200,
) -> int:
    """
    Find the optimal frame offset between the two data sets by looking at the average deviation of the z axis.
    :return: The optimal frame offset for the base
    """
    base_offset = 0
    lowest_deviation = float("inf")
    for offset in range(min(len(base_data) - 2, max_offset)):
        # Calculate the deviations
        deviations = calculate_deviations(
            base_data[offset:],
            diff_data,
            {0: 15},
            base_time_offset=base_data[offset].time_ms,
            diff_time_offset=diff_data[0].time_ms,
        )
        # The average deviation of the z axis
        deviation = deviations.get(0).z_abs
        if deviation < lowest_deviation:
            lowest_deviation = deviation
            print(f"Base offset: {offset}, Average z-axis deviation: {deviation}")
            base_offset = offset

    return base_offset


def find_optimal_diff_offset(
    base_data: list[Frame],
    diff_data: list[Frame],
    max_offset: int = 200,
) -> int:
    """
    Find the optimal frame offset between the two data sets by looking at the average deviation of the z axis
    :return: The optimal frame offset for the diff data
    """
    diff_offset = 0
    lowest_deviation = float("inf")
    for offset in range(min(len(diff_data) - 2, max_offset)):
        # Calculate the deviations
        deviations = calculate_deviations(
            base_data,
            diff_data[offset:],
            {0: 15},
            base_time_offset=base_data[0].time_ms,
            diff_time_offset=diff_data[offset].time_ms,
        )
        # The average deviation of the z axis
        deviation = deviations.get(0).z_abs
        if deviation < lowest_deviation:
            lowest_deviation = deviation
            print(f"Diff offset: {offset}, Average z-axis deviation: {deviation}")
            diff_offset = offset

    return diff_offset
