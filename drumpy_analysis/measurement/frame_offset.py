from measurement.deviation import calculate_deviations
from measurement.frame import Frame
from measurement.measurement import Measurement


def remove_time_offset(frames: list[Frame]):
    """
    Remove the time offset from the frames
    """
    time_offset = frames[0].time_ms
    frames[0].time_ms = 0
    for frame in frames[1:]:
        frame.time_ms -= time_offset


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


def frame_offsets(
    base_data: list[Frame],
    diff_data: list[Frame],
    measurement: Measurement,
):
    assert (
        measurement.base_frame_offset is not None
        or measurement.diff_frame_offset is not None
    ), "Either the base or diff frame offset should be set to align the frames."

    if measurement.base_frame_offset is None:
        base_offset = find_optimal_base_offset(
            base_data,
            diff_data,
        )
        print(f"Base offset: {base_offset}")
        measurement.base_frame_offset = base_offset
        del base_data[:base_offset]
    else:
        del base_data[: measurement.base_frame_offset]

    if measurement.diff_frame_offset is None:
        diff_offset = find_optimal_diff_offset(
            base_data,
            diff_data,
        )
        print(f"Diff offset: {diff_offset}")
        measurement.diff_frame_offset = diff_offset
        del diff_data[:diff_offset]
    else:
        del diff_data[: measurement.diff_frame_offset]

    remove_time_offset(base_data)
    remove_time_offset(diff_data)
