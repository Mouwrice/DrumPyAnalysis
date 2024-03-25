from drumpy_analysis.graphs.deviations_boxplot import deviations_boxplot
from drumpy_analysis.graphs.trajectory_lineplot import plot_trajectories
from drumpy_analysis.measurement.deviation import (
    compute_deviations_from_measurement,
    write_deviations,
)
from drumpy_analysis.measurement.frame import Frame, frames_from_csv, get_marker_centers
from drumpy_analysis.measurement.measurement import Measurement


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


def calculate_base_center(frames: list[Frame], mapping: dict[int, int]):
    """
    Calculate the center of the base recording
    """
    centers = {}
    for key, value in mapping.items():
        x = 0
        y = 0
        z = 0
        for frame in frames:
            row = frame.rows[key]
            x += row.x
            y += row.y
            z += row.z
        centers[key] = (x / len(frames), y / len(frames), z / len(frames))
    return centers


def analyze(measurement: Measurement):
    print(f"\n\n --- Analyzing {measurement.plot_prefix} --- \n")
    base_data = frames_from_csv(measurement.base_recording)
    diff_data = frames_from_csv(measurement.diff_recording, measurement.unit_conversion)

    apply_axis_transformations(diff_data, measurement)

    measurement.base_centers = calculate_base_center(base_data, measurement.mapping)

    # remove_average_offset(
    #     base_data, diff_data, measurement.mapping, measurement.dominant_fps
    # )
    #
    # frame_offsets(base_data, diff_data, measurement)
    #
    # remove_average_offset(
    #     base_data, diff_data, measurement.mapping, measurement.dominant_fps
    # )
    #
    # apply_diff_stretch(base_data, diff_data, measurement)
    #
    # remove_average_offset(
    #     base_data, diff_data, measurement.mapping, measurement.dominant_fps
    # )

    measurement.diff_centers = get_marker_centers(diff_data, measurement.mapping)

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
    # Measurement(
    #     base_recording="data/asil_01/qtm.csv",
    #     diff_recording="data/asil_01/front/LITE.csv",
    #     output_prefxix="data/asil_01/front/",
    #     mapping={0: 15},
    #     diff_frame_offset=71,
    #     plot_prefix="mediapipe_asil_01_front_LITE",
    # ),
    # Measurement(
    #     base_recording="data/asil_01/qtm.csv",
    #     diff_recording="data/asil_01/front/FULL.csv",
    #     output_prefxix="data/asil_01/front/",
    #     mapping={0: 15},
    #     diff_frame_offset=71,
    #     plot_prefix="mediapipe_asil_01_front_FULL",
    # ),
    # Measurement(
    #     base_recording="data/asil_01/qtm.csv",
    #     diff_recording="data/asil_01/front/FULL.csv",
    #     output_prefxix="data/asil_01/front/",
    #     mapping=qtm_to_mediapipe,
    #     diff_frame_offset=71,
    #     plot_prefix="mediapipe_asil_01_front_FULL",
    # ),
    # Measurement(
    #     base_recording="data/asil_01/qtm.csv",
    #     diff_recording="data/asil_01/front/HEAVY.csv",
    #     output_prefxix="data/asil_01/front/",
    #     mapping={0: 15},
    #     diff_frame_offset=71,
    #     plot_prefix="mediapipe_asil_01_front_HEAVY",
    # ),
    Measurement(
        base_recording="data/asil_01/qtm.csv",
        diff_recording="data/asil_01/qtm.csv",
        output_prefxix="data/asil_01/",
        mapping={0: 0},
        diff_frame_offset=0,
        base_axis_rotation=0,
        unit_conversion=1,
        diff_axis_reorder=False,
        plot_prefix="qtm_qtm_offset",
        diff_axis_stretch=(1, 1, 1),
        diff_axis_offset=(45.525611, 8.026620, 12.582678),
        diff_flip_axis=(False, False, False),
    ),
]

if __name__ == "__main__":
    for measure in measurements:
        analyze(measure)
