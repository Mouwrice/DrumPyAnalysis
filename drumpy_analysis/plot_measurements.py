from copy import deepcopy

from scipy.spatial.transform import Rotation

from drumpy_analysis.measurement.frame import Frame, frames_from_csv
from graphs.deviations_boxplot import deviations_boxplot
from graphs.trajectory_lineplot import plot_trajectories
from measurement.measurement import Measurement


def get_closest_frame_index(frames: list[Frame], frame_number: int) -> int:
    """
    Get the index of the frame with the closest frame number
    :param frames:
    :param frame_number:
    :return:
    """
    return min(range(len(frames)), key=lambda i: abs(frames[i].frame - frame_number))


def remove_average_offset(
    base_data: list[Frame], diff_data: list[Frame], mapping: dict[int, int]
):
    """
    Remove the average offset of the diff data compared to the base data.
    Per axis.
    """
    assert len(base_data) == len(diff_data), "Data length does not match"

    for base_marker, diff_marker in mapping.items():
        avg_offset_x = 0
        avg_offset_y = 0
        avg_offset_z = 0
        for base_frame, diff_frame in zip(base_data, diff_data):
            avg_offset_x += (
                diff_frame.rows[diff_marker].x - base_frame.rows[base_marker].x
            )
            avg_offset_y += (
                diff_frame.rows[diff_marker].y - base_frame.rows[base_marker].y
            )
            avg_offset_z += (
                diff_frame.rows[diff_marker].z - base_frame.rows[base_marker].z
            )

        avg_offset_x /= len(base_data)
        avg_offset_y /= len(base_data)
        avg_offset_z /= len(base_data)
        print("Average offsets", avg_offset_x, avg_offset_y, avg_offset_z)
        # Apply the offset
        for diff_frame in diff_data:
            diff_frame.rows[diff_marker].x -= avg_offset_x
            diff_frame.rows[diff_marker].y -= avg_offset_y
            diff_frame.rows[diff_marker].z -= avg_offset_z


def arrange_measurement_data(
    base_data: list[Frame],
    diff_data: list[Frame],
    base_frame_offset,
    diff_frame_offset,
) -> (list[Frame], list[Frame]):
    """
    Given two lists of frames, aligns the frames and plots the data by duplicating the frames if necessary
    """

    assert len(base_data) > 0, "No frames found in base data"
    assert len(diff_data) > 0, "No frames found in diff data"

    base_frame_offset = max(base_frame_offset, base_data[0].frame)
    print("base_frame_offset", base_frame_offset)
    diff_frame_offset = max(diff_frame_offset, diff_data[0].frame)
    print("diff_frame_offset", diff_frame_offset)

    base_idx = get_closest_frame_index(base_data, base_frame_offset)
    diff_idx = get_closest_frame_index(diff_data, diff_frame_offset)
    base_time_offset = base_data[base_idx].time_ms
    diff_time_offset = diff_data[diff_idx].time_ms

    base_frame = base_data[base_idx]
    diff_frame = diff_data[diff_idx]
    base_arranged = []
    diff_arranged = []
    while base_idx < len(base_data) - 1 and diff_idx < len(diff_data) - 1:
        base_next_frame = base_data[base_idx + 1]
        diff_next_frame = diff_data[diff_idx + 1]
        base_time = base_frame.time_ms - base_time_offset
        diff_time = diff_frame.time_ms - diff_time_offset

        if base_time < diff_time:
            base_idx += 1
            base_frame = base_next_frame
            diff_frame = deepcopy(diff_frame)
        elif base_time > diff_time:
            diff_idx += 1
            diff_frame = diff_next_frame
            base_frame = deepcopy(base_frame)
        else:
            base_idx += 1
            diff_idx += 1
            base_frame = base_next_frame
            diff_frame = diff_next_frame

        base_arranged.append(base_frame)
        diff_arranged.append(diff_frame)

    assert len(base_arranged) == len(
        diff_arranged
    ), "Length of base and diff data does not match"

    return base_arranged, diff_arranged


def apply_offset_scale_rotation(frames: list[Frame], measurement: Measurement):
    """
    Apply offset, scale and rotation to the frames
    """
    rotation = Rotation.from_euler("z", measurement.axis_rotation, degrees=True)

    for frame in frames:
        for row in frame.rows:
            # First apply the reordering
            if measurement.axis_reorder:
                row.x, row.y, row.z = row.z, row.x, row.y

            # Apply the scale
            row.x *= measurement.axis_scale[0]
            row.y *= measurement.axis_scale[1]
            row.z *= measurement.axis_scale[2]

            # Apply the offset
            row.x += measurement.axis_offset[0]
            row.y += measurement.axis_offset[1]
            row.z += measurement.axis_offset[2]

            # Then apply the rotation
            row.x, row.y, row.z = rotation.apply([row.x, row.y, row.z])


def plot_measurement(measurement: Measurement):
    """
    Plots the measurement
    """
    base_data = frames_from_csv(measurement.base_recording)
    diff_data = frames_from_csv(measurement.diff_recording, measurement.unit_conversion)

    apply_offset_scale_rotation(diff_data, measurement)

    base_arranged, diff_arranged = arrange_measurement_data(
        base_data,
        diff_data,
        measurement.base_frame_offset,
        measurement.diff_frame_offset,
    )

    remove_average_offset(base_arranged, diff_arranged, measurement.mapping)

    plot_trajectories(base_arranged, diff_arranged, measurement, show_plot=True)
    deviations_boxplot(base_arranged, diff_arranged, measurement)


qtm_to_mediapipe = {
    0: 15,  # left wrist
    1: 16,  # right wrist
    2: 19,  # left index
    3: 20,  # right index
    4: 31,  # left foot index
    5: 32,  # right foot index
}

measurements = [
    Measurement(
        base_recording="data/multicam_asil_01/qtm_multicam_asil_01.csv",
        diff_recording="data/multicam_asil_01/mediapipe_multicam_asil_01_front_LITE_async_video.csv",
        unit_conversion=1000,
        base_frame_offset=100,
        diff_frame_offset=100,
        output_prefxix="data/multicam_asil_01/",
        # axis_offset=(0, 0, 0),
        axis_offset=(0, 0, 0),
        axis_scale=(-0.5, 4, -2),
        axis_rotation=0,
        axis_reorder=True,
        mapping={0: 15},
        plot_prefix="multicam_asil_01_front_LITE_async",
        base_label="QTM",
        diff_label="Mediapipe",
    ),
]

if __name__ == "__main__":
    for measure in measurements:
        plot_measurement(measure)
