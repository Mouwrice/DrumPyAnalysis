from dataclasses import dataclass

from measurement.frame import Frame


@dataclass
class Deviation:
    x: float
    y: float
    z: float
    euclidean_distance: float


def calculate_deviations(
    base: list[Frame],
    diff: list[Frame],
    mapping: dict[int, int],
    base_time_offset: int = 0,
    diff_time_offset: int = 0,
) -> dict[int, Deviation]:
    """
    Calculate the absolute deviation between the base and diff data
    The two data sets can have different lengths and different time stamps
    :return: For each marker, a tuple of deviations being (x, y, z, Euclidean distance)
    """
    base_index = 0
    diff_index = 0
    base_frame = base[base_index]
    diff_frame = diff[diff_index]
    deviations = {}
    for key in mapping.keys():
        deviations[key] = Deviation(0, 0, 0, 0)

    count = 0

    while base_index < len(base) - 1 and diff_index < len(diff) - 1:
        count += 1

        for base_marker, diff_marker in mapping.items():
            base_row = base_frame.rows[base_marker]
            diff_row = diff_frame.rows[diff_marker]
            deviations[base_marker].x += abs(diff_row.x - base_row.x)
            deviations[base_marker].y += abs(diff_row.y - base_row.y)
            deviations[base_marker].z += abs(diff_row.z - base_row.z)
            deviations[base_marker].euclidean_distance += (
                (diff_row.x - base_row.x) ** 2
                + (diff_row.y - base_row.y) ** 2
                + (diff_row.z - base_row.z) ** 2
            ) ** 0.5

        # The time stamps are not aligned, the next frame is the frame with the closest time stamp
        base_time = base_frame.time_ms - base_time_offset
        diff_time = diff_frame.time_ms - diff_time_offset
        next_base_time = base[base_index + 1].time_ms - base_time_offset
        next_diff_time = diff[diff_index + 1].time_ms - diff_time_offset
        if next_base_time < next_diff_time:
            base_index += 1
            base_frame = base[base_index]
            # Find the diff frame that is closest in time
            if abs(next_base_time - diff_time) > abs(next_base_time - next_diff_time):
                diff_index += 1
                diff_frame = diff[diff_index]
        else:
            diff_index += 1
            diff_frame = diff[diff_index]
            # Find the base frame that is closest in time
            if abs(next_diff_time - base_time) > abs(next_diff_time - next_base_time):
                base_index += 1
                base_frame = base[base_index]

    for key, value in mapping.items():
        deviations[key].x /= count
        deviations[key].y /= count
        deviations[key].z /= count
        deviations[key].euclidean_distance /= count

    return deviations
