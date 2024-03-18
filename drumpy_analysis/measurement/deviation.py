from dataclasses import dataclass
from typing import TextIO

import pandas
from scipy.spatial.transform import Rotation

from measurement.frame import Frame
from measurement.measurement import Measurement


@dataclass
class Deviation:
    offset_x: float
    offset_y: float
    offset_z: float
    deviation_x: float
    deviation_y: float
    deviation_z: float
    euclidean_distance: float

    def add(self, deviation: "Deviation"):
        self.offset_x += deviation.offset_x
        self.offset_y += deviation.offset_y
        self.offset_z += deviation.offset_z
        self.deviation_x += deviation.deviation_x
        self.deviation_y += deviation.deviation_y
        self.deviation_z += deviation.deviation_z
        self.euclidean_distance += deviation.euclidean_distance

    def divide(self, count: int):
        self.offset_x /= count
        self.offset_y /= count
        self.offset_z /= count
        self.deviation_x /= count
        self.deviation_y /= count
        self.deviation_z /= count
        self.euclidean_distance /= count


def compute_deviations_from_measurement(
    base_data: list[Frame],
    diff_data: list[Frame],
    measurement: Measurement,
    deviation_lists: dict[int, list[Deviation]] = None,
):
    compute_devations(
        base_data,
        diff_data,
        measurement.mapping,
        measurement.base_frame_offset,
        measurement.diff_frame_offset,
        measurement.base_axis_rotation,
        measurement.diff_axis_stretch,
        measurement.diff_stretch_centers,
        deviation_lists=deviation_lists,
    )


def compute_average_deviation(
    base: list[Frame],
    diff: list[Frame],
    mapping: dict[int, int],
    base_offset: int = 0,
    diff_offset: int = 0,
    base_rotation: float = 0,
    diff_axis_stretch: tuple[float, float, float] = (1, 1, 1),
    diff_axis_centers: dict[int, tuple[float, float, float]] = (0, 0, 0),
) -> Deviation:
    """
    Calculate the average deviation between the base and diff data.
    The two data sets can have different lengths and different time stamps.
    But averages over all markers.
    Transformations on the diff data can be specified but are not directly appleid to the data.
    :param base: The base data
    :param diff: The diff data
    :param mapping: The mapping between the base and diff data
    :param base_offset: The time offset for the base data
    :param diff_offset: The time offset for the diff data
    :param base_rotation: The rotation to apply to the base data around the vertical (z) axis, default is 0
    :param diff_axis_stretch: The stretch to apply to the diff data, default is (1, 1, 1), (x, y, z)
    :param diff_axis_centers: The center of the stretct, values that lie on this point are not changed.
    When the stretch is zero, all points converge to this center.
    The center is specified for each marker.
    away from this point. The center is specified for each marker.
    """

    deviations = compute_devations(
        base,
        diff,
        mapping,
        base_offset,
        diff_offset,
        base_rotation,
        diff_axis_stretch,
        diff_axis_centers,
    )

    average = Deviation(0, 0, 0, 0, 0, 0, 0)
    for key, value in mapping.items():
        average.add(deviations[key])

    average.divide(len(mapping))
    return average


def compute_devations(
    base: list[Frame],
    diff: list[Frame],
    mapping: dict[int, int],
    base_offset: int = 0,
    diff_offset: int = 0,
    base_rotation: float | None = None,
    diff_axis_stretch: tuple[float, float, float] = (1, 1, 1),
    diff_axis_centers: dict[int, tuple[float, float, float]] = None,
    deviation_lists: dict[int, list[Deviation]] = None,
) -> dict[int, Deviation]:
    """
    Calculate the absolute deviation between the base and diff data
    The two data sets can have different lengths and different time stamps
    :param base: The base data
    :param diff: The diff data
    :param mapping: The mapping between the base and diff data
    :param base_offset: The time offset for the base data
    :param diff_offset: The time offset for the diff data
    :param base_rotation: The rotation to apply to the base data around the vertical (z) axis, default is 0
    :param diff_axis_stretch: The stretch to apply to the diff data, default is (1, 1, 1), (x, y, z)
    :param diff_axis_centers: The center of the stretct, values that lie on this point are not changed.
    When the stretch is zero, all points converge to this center.
    The center is specified for each marker.
    :param deviation_lists: Pass a dictionary to store the deviations for each individual frame.
    A deviation is not particularly assigned to a frame, as we perform the computation over all combined frames.
    :return: For each marker, a Deviation
    """
    base_index = 0
    diff_index = 0
    base_frame = base[base_index]
    diff_frame = diff[diff_index]
    deviations = {}
    for key in mapping.keys():
        deviations[key] = Deviation(0, 0, 0, 0, 0, 0, 0)

    rotation = Rotation.from_euler("z", base_rotation, degrees=True)

    count = 0

    while base_index < len(base) - 1 and diff_index < len(diff) - 1:
        count += 1

        for base_marker, diff_marker in mapping.items():
            base_row = base_frame.rows[base_marker]
            if base_rotation is not None:
                base_x, base_y, base_z = rotation.apply(
                    [base_row.x, base_row.y, base_row.z]
                )
            else:
                base_x = base_row.x
                base_y = base_row.y
                base_z = base_row.z

            diff_row = diff_frame.rows[diff_marker]

            if diff_axis_centers is not None:
                center_x = diff_axis_centers[diff_marker][0]
                center_y = diff_axis_centers[diff_marker][1]
                center_z = diff_axis_centers[diff_marker][2]
                diff_x = (diff_row.x - center_x) * diff_axis_stretch[0] + center_x
                diff_y = (diff_row.y - center_y) * diff_axis_stretch[1] + center_y
                diff_z = (diff_row.z - center_z) * diff_axis_stretch[2] + center_z
            else:
                diff_x = diff_row.x
                diff_y = diff_row.y
                diff_z = diff_row.z

            x = base_x - diff_x
            y = base_y - diff_y
            z = base_z - diff_z

            deviation = Deviation(
                x, y, z, abs(x), abs(y), abs(z), (x**2 + y**2 + x**2) ** 0.5
            )

            deviations[base_marker].add(deviation)

            if deviation_lists is not None:
                if diff_marker not in deviation_lists:
                    deviation_lists[diff_marker] = []
                deviation_lists[diff_marker].append(deviation)

        # The time stamps are not aligned, the next frame is the frame with the closest time stamp
        base_time = base_frame.time_ms - base_offset
        diff_time = diff_frame.time_ms - diff_offset
        next_base_time = base[base_index + 1].time_ms - base_offset
        next_diff_time = diff[diff_index + 1].time_ms - diff_offset
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
        deviations[key].divide(count)

    return deviations


def remove_average_offset(
    base_data: list[Frame],
    diff_data: list[Frame],
    mapping: dict[int, int],
):
    """
    Remove the average offset of the diff data compared to the base data.
    Per axis.
    """
    deviations = compute_devations(base_data, diff_data, mapping)
    for key, value in mapping.items():
        for frame in diff_data:
            frame.rows[value].x += deviations[key].offset_x
            frame.rows[value].y += deviations[key].offset_y
            frame.rows[value].z += deviations[key].offset_z


def write_deviations(
    deviation_lists: dict[int, list[Deviation]],
    file: TextIO,
):
    file.write("\n\nDeviations:\n")

    for key, value in deviation_lists.items():
        file.write(f"Diff Marker {key}:\n")

        # Convert the list to a pandas dataframe
        df = pandas.DataFrame(value)

        # Write the dataframe to the file
        file.write(df.describe().to_string())

        file.write("\n\n")
