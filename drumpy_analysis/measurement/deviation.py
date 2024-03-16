from dataclasses import dataclass

from measurement.frame import Frame


@dataclass
class Deviation:
    x: float
    y: float
    z: float
    x_abs: float
    y_abs: float
    z_abs: float
    euclidean_distance: float


def average_absolute_deviation(
    base: list[Frame],
    diff: list[Frame],
    mapping: dict[int, int],
    base_time_offset: int = 0,
    diff_time_offset: int = 0,
    scale_diff: tuple[float, float, float] = (1, 1, 1),
    scale_centers_diff: dict[int, tuple[float, float, float]] = (0, 0, 0),
) -> Deviation:
    """
    Calculate the average deviation between the base and diff data.
    The two data sets can have different lengths and different time stamps.
    But averages over all markers.
    Transformations on the diff data can be specified but are not directly appleid to the data.
    :param base: The base data
    :param diff: The diff data
    :param mapping: The mapping between the base and diff data
    :param base_time_offset: The time offset for the base data
    :param diff_time_offset: The time offset for the diff data
    :param scale_diff: The scale to apply to the diff data, default is (1, 1, 1), (x, y, z)
    :param scale_centers_diff: The center of the scale, values that lie on this point are not changed, other values are scaled
    away from this point. The center is specified for each marker.
    """

    deviations = calculate_deviations(
        base,
        diff,
        mapping,
        base_time_offset,
        diff_time_offset,
        scale_diff,
        scale_centers_diff,
    )

    average = Deviation(0, 0, 0, 0, 0, 0, 0)
    for key, value in mapping.items():
        average.x += deviations[key].x
        average.y += deviations[key].y
        average.z += deviations[key].z
        average.x_abs += deviations[key].x_abs
        average.y_abs += deviations[key].y_abs
        average.z_abs += deviations[key].z_abs
        average.euclidean_distance += deviations[key].euclidean_distance
    average.x /= len(mapping)
    average.y /= len(mapping)
    average.z /= len(mapping)
    average.x_abs /= len(mapping)
    average.y_abs /= len(mapping)
    average.z_abs /= len(mapping)
    average.euclidean_distance /= len(mapping)
    return average


def calculate_deviations(
    base: list[Frame],
    diff: list[Frame],
    mapping: dict[int, int],
    base_time_offset: int = 0,
    diff_time_offset: int = 0,
    scale_diff: tuple[float, float, float] = (1, 1, 1),
    scale_centers_diff: dict[int, tuple[float, float, float]] = None,
) -> dict[int, Deviation]:
    """
    Calculate the absolute deviation between the base and diff data
    The two data sets can have different lengths and different time stamps
    :param base: The base data
    :param diff: The diff data
    :param mapping: The mapping between the base and diff data
    :param base_time_offset: The time offset for the base data
    :param diff_time_offset: The time offset for the diff data
    :param scale_diff: The scale to apply to the diff data, default is (1, 1, 1), (x, y, z)
    :param scale_centers_diff: The center of the scale, values that lie on this point are not changed, other values are scaled
    away from this point. The center is specified for each marker.
    :return: For each marker, a Deviation
    """
    base_index = 0
    diff_index = 0
    base_frame = base[base_index]
    diff_frame = diff[diff_index]
    deviations = {}
    for key in mapping.keys():
        deviations[key] = Deviation(0, 0, 0, 0, 0, 0, 0)

    count = 0

    while base_index < len(base) - 1 and diff_index < len(diff) - 1:
        count += 1

        for base_marker, diff_marker in mapping.items():
            base_row = base_frame.rows[base_marker]
            diff_row = diff_frame.rows[diff_marker]

            if scale_centers_diff is not None:
                diff_x = (diff_row.x - scale_centers_diff[diff_marker][0]) * scale_diff[
                    0
                ] + diff_row.x
                diff_y = (diff_row.y - scale_centers_diff[diff_marker][1]) * scale_diff[
                    1
                ] + diff_row.y
                diff_z = (diff_row.z - scale_centers_diff[diff_marker][2]) * scale_diff[
                    2
                ] + diff_row.z
            else:
                diff_x = diff_row.x
                diff_y = diff_row.y
                diff_z = diff_row.z

            x = base_row.x - diff_x
            y = base_row.y - diff_y
            z = base_row.z - diff_z

            deviations[base_marker].x += x
            deviations[base_marker].y += y
            deviations[base_marker].z += z
            deviations[base_marker].x_abs += abs(x)
            deviations[base_marker].y_abs += abs(y)
            deviations[base_marker].z_abs += abs(z)
            deviations[base_marker].euclidean_distance += (x**2 + y**2 + x**2) ** 0.5

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
        deviations[key].x_abs /= count
        deviations[key].y_abs /= count
        deviations[key].z_abs /= count
        deviations[key].euclidean_distance /= count

    return deviations
