from drumpy_analysis.measurement.frame import Frame, frames_from_csv
from graphs.deviations_boxplot import deviations_boxplot
from graphs.trajectory_lineplot import plot_trajectories
from measurement.deviation import (
    remove_average_offset,
    compute_deviations_from_measurement,
    write_deviations,
)
from measurement.find_optimal_stretch import apply_diff_stretch
from measurement.frame_offset import frame_offsets
from measurement.measurement import Measurement


def apply_axis_transformations(frames: list[Frame], measurement: Measurement):
    """
    Transform the axis of the diff data
    """
    # rotation = Rotation.from_euler("z", measurement.base_axis_rotation, degrees=True)
    for frame in frames:
        for row in frame.rows:
            # First apply the reordering
            if measurement.diff_axis_reorder:
                row.x, row.y, row.z = row.z, row.x, row.y

            # Flip the axis of diff
            if measurement.diff_flip_axis[0]:
                row.x *= -1
            if measurement.diff_flip_axis[1]:
                row.y *= -1
            if measurement.diff_flip_axis[2]:
                row.z *= -1

            # Apply the offset
            row.x += measurement.diff_axis_offset[0]
            row.y += measurement.diff_axis_offset[1]
            row.z += measurement.diff_axis_offset[2]


def plot_measurement(measurement: Measurement):
    """
    Plots the measurement
    """
    base_data = frames_from_csv(measurement.base_recording)
    diff_data = frames_from_csv(measurement.diff_recording, measurement.unit_conversion)

    apply_axis_transformations(diff_data, measurement)

    # 1. Remove the average offset
    remove_average_offset(base_data, diff_data, measurement.mapping)

    # 2. Apply or find the frame offset
    frame_offsets(base_data, diff_data, measurement)

    # 4. Apply or find the scale and rotation
    # apply_base_rotation(base_data, diff_data, measurement)
    apply_diff_stretch(base_data, diff_data, measurement)

    plot_trajectories(base_data, diff_data, measurement, show_plot=True)

    deviations = {}
    compute_deviations_from_measurement(base_data, diff_data, measurement, deviations)

    deviations_boxplot(deviations, measurement)

    # Write the obtained results to a file
    with open(
        f"{measurement.output_prefxix}{measurement.plot_prefix}_results.txt", "w"
    ) as f:
        measurement.write(f)
        write_deviations(deviations, f)


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
        base_recording="data/asil_01/qtm.csv",
        diff_recording="data/asil_01/front/LITE.csv",
        output_prefxix="data/asil_01/front/",
        mapping={0: 15},
        diff_frame_offset=71,
        plot_prefix="mediapipe_asil_01_front_LITE",
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
    #     output_prefxix="data/multicam_asil_01/",
    #     mapping={0: 15},
    #     plot_prefix="mediapipe_multicam_asil_01_front_HEAVY",
    # ),
    # Measurement(
    #     base_recording="data/multicam_asil_01/qtm_multicam_asil_01.csv",
    #     diff_recording="data/multicam_asil_01/mediapipe_multicam_asil_01_left_HEAVY.csv",
    #     output_prefxix="data/multicam_asil_01/",
    #     mapping={0: 15},
    #     base_axis_rotation=180,
    #     # diff_frame_offset=119,
    #     plot_prefix="mediapipe_multicam_asil_01_left_HEAVY",
    # ),
    # Measurement(
    #     base_recording="data/multicam_asil_01/qtm_multicam_asil_01.csv",
    #     diff_recording="data/multicam_asil_01/mediapipe_multicam_asil_01_right_HEAVY.csv",
    #     output_prefxix="data/multicam_asil_01/",
    #     mapping={0: 15},
    #     diff_frame_offset=183,
    #     base_axis_rotation=40,
    #     # diff_axis_stretch=(0.5, 3.5, 2),
    #     plot_prefix="mediapipe_multicam_asil_01_right_HEAVY",
    # ),
]

if __name__ == "__main__":
    for measure in measurements:
        plot_measurement(measure)
