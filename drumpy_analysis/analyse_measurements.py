from scipy.spatial.transform import Rotation

from drumpy_analysis.measurement.frame import Frame, frames_from_csv
from graphs.trajectory_lineplot import plot_trajectories
from measurement.deviation import calculate_deviations
from measurement.find_optimal_offset import (
    find_optimal_diff_offset,
    find_optimal_base_offset,
)
from measurement.measurement import Measurement


def remove_time_offset(frames: list[Frame], time_offset: int):
    """
    Remove the time offset from the frames
    """
    for frame in frames:
        frame.time_ms -= time_offset


def remove_average_offset(
    base_data: list[Frame],
    diff_data: list[Frame],
    mapping: dict[int, int],
):
    """
    Remove the average offset of the diff data compared to the base data.
    Per axis.
    """
    deviations = calculate_deviations(base_data, diff_data, mapping)
    for key, value in mapping.items():
        print(f"Average deviation for marker {key} and {value}: {deviations[key]}")
        for frame in diff_data:
            frame.rows[value].x -= deviations[key].x
            frame.rows[value].y -= deviations[key].y
            frame.rows[value].z -= deviations[key].z


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

    # 1. Remove the average offset
    remove_average_offset(base_data, diff_data, measurement.mapping)

    assert (
        measurement.base_frame_offset is not None
        or measurement.diff_frame_offset is not None
    ), "Frame offset must be set"

    # 2. Apply or find the frame offset
    if measurement.base_frame_offset is None:
        base_offset = find_optimal_base_offset(
            base_data,
            diff_data,
        )
        print(f"Base offset: {base_offset}")
        base_data = base_data[base_offset:]
        remove_time_offset(base_data, base_data[0].time_ms)
    else:
        base_data = base_data[measurement.base_frame_offset :]
        time_offset = base_data[0].time_ms
        remove_time_offset(diff_data, time_offset)

    if measurement.diff_frame_offset is None:
        diff_offset = find_optimal_diff_offset(
            base_data,
            diff_data,
        )
        print(f"Diff offset: {diff_offset}")
        diff_data = diff_data[diff_offset:]
        remove_time_offset(diff_data, diff_data[0].time_ms)

    else:
        diff_data = diff_data[measurement.diff_frame_offset :]
        time_offset = diff_data[0].time_ms
        remove_time_offset(base_data, time_offset)

    # 3. Remove the average offset again, now that the frames are aligned
    remove_average_offset(base_data, diff_data, measurement.mapping)

    plot_trajectories(base_data, diff_data, measurement, show_plot=True)
    # deviations_boxplot(base_data, diff_data, measurement, file=file)


qtm_to_mediapipe = {
    0: 15,  # left wrist
    1: 16,  # right wrist
    2: 19,  # left index
    3: 20,  # right index
    4: 31,  # left foot index
    5: 32,  # right foot index
}

qtm_to_mediapipe_compact = {
    0: 15,  # left wrist
    4: 31,  # left foot index
}

measurements = [
    Measurement(
        base_recording="data/multicam_asil_01/qtm_multicam_asil_01.csv",
        diff_recording="data/multicam_asil_01/mediapipe_multicam_asil_01_front_LITE.csv",
        output_prefxix="data/multicam_asil_01/",
        mapping={0: 15},
        plot_prefix="mediapipe_multicam_asil_01_front_LITE",
        base_label="QTM",
        diff_label="Mediapipe",
    ),
    # Measurement(
    #     base_recording="data/multicam_asil_01/qtm_multicam_asil_01.csv",
    #     diff_recording="data/multicam_asil_01/mediapipe_multicam_asil_01_front_LITE.csv",
    #     unit_conversion=1000,
    #     base_frame_offset=100,
    #     diff_frame_offset=100,
    #     output_prefxix="data/multicam_asil_01/",
    #     # axis_offset=(0, 0, 0),
    #     axis_offset=(0, 0, 0),
    #     axis_scale=(-0.5, 4, -2),
    #     axis_rotation=0,
    #     axis_reorder=True,
    #     mapping={2: 31},
    #     plot_prefix="mediapipe_multicam_asil_01_front_LITE_4_31",
    #     base_label="QTM",
    #     diff_label="Mediapipe",
    # ),
    # Measurement(
    #     base_recording="data/multicam_asil_01/qtm_multicam_asil_01.csv",
    #     diff_recording="data/multicam_asil_01/mediapipe_multicam_asil_01_front_FULL.csv",
    #     unit_conversion=1000,
    #     base_frame_offset=100,
    #     diff_frame_offset=100,
    #     output_prefxix="data/multicam_asil_01/",
    #     # axis_offset=(0, 0, 0),
    #     axis_offset=(0, 0, 0),
    #     axis_scale=(-0.5, 4, -2),
    #     axis_rotation=0,
    #     axis_reorder=True,
    #     mapping={0: 15},
    #     plot_prefix="multicam_asil_01_front_FULL",
    #     base_label="QTM",
    #     diff_label="Mediapipe",
    # ),
    # Measurement(
    #     base_recording="data/multicam_asil_01/qtm_multicam_asil_01.csv",
    #     diff_recording="data/multicam_asil_01/mediapipe_multicam_asil_01_front_HEAVY.csv",
    #     unit_conversion=1000,
    #     base_frame_offset=100,
    #     diff_frame_offset=100,
    #     output_prefxix="data/multicam_asil_01/",
    #     # axis_offset=(0, 0, 0),
    #     axis_offset=(0, 0, 0),
    #     axis_scale=(-0.5, 4, -2),
    #     axis_rotation=0,
    #     axis_reorder=True,
    #     mapping={0: 15},
    #     plot_prefix="mediapipe_multicam_asil_01_front_HEAVY",
    #     base_label="QTM",
    #     diff_label="Mediapipe",
    # ),
    # Measurement(
    #     base_recording="data/multicam_asil_01/qtm_multicam_asil_01.csv",
    #     diff_recording="data/multicam_asil_01/mediapipe_multicam_asil_01_left_HEAVY.csv",
    #     unit_conversion=1000,
    #     base_frame_offset=100,
    #     diff_frame_offset=147,
    #     output_prefxix="data/multicam_asil_01/",
    #     # axis_offset=(0, 0, 0),
    #     axis_offset=(0, 0, 0),
    #     axis_scale=(-0.5, 4, -2),
    #     axis_rotation=30,
    #     axis_reorder=True,
    #     mapping={0: 15},
    #     plot_prefix="mediapipe_multicam_asil_01_left_HEAVY",
    #     base_label="QTM",
    #     diff_label="Mediapipe",
    # ),
    # Measurement(
    #     base_recording="data/multicam_asil_01/qtm_multicam_asil_01.csv",
    #     diff_recording="data/multicam_asil_01/mediapipe_multicam_asil_01_right_HEAVY.csv",
    #     unit_conversion=1000,
    #     base_frame_offset=100,
    #     diff_frame_offset=214,
    #     output_prefxix="data/multicam_asil_01/",
    #     # axis_offset=(0, 0, 0),
    #     axis_offset=(0, 0, 0),
    #     axis_scale=(-0.5, 5, -1.7),
    #     axis_rotation=30,
    #     axis_reorder=True,
    #     mapping={0: 15},
    #     plot_prefix="mediapipe_multicam_asil_01_right_HEAVY",
    #     base_label="QTM",
    #     diff_label="Mediapipe",
    # ),
]

if __name__ == "__main__":
    for measure in measurements:
        plot_measurement(measure)
