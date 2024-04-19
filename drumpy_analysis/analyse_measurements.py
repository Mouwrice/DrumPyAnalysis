from drumpy_analysis.graphs.deviations_boxplot import deviations_boxplot
from drumpy_analysis.measurement.deviation import (
    compute_deviations_from_measurement,
    write_deviations,
    remove_average_offset,
)
from drumpy_analysis.measurement.frame import Frame, get_marker_centers
from drumpy_analysis.measurement.measurement import Measurement
from drumpy_analysis.measurement.find_optimal_stretch import apply_diff_stretch
from drumpy_analysis.measurement.frame_offset import frame_offsets

from drumpy.mediapipe_pose.mediapipe_markers import MarkerEnum

from drumpy_analysis.qtm.qtm_measurement import QTM


def apply_axis_transformations(frames: list[Frame], measurement: Measurement) -> None:
    """
    Transform the axis of the diff data
    """
    # rotation = Rotation.from_euler("z", measurement.base_axis_rotation, degrees=True)
    for frame in frames:
        for marker in frame.markers.values():
            # First apply the reordering
            if measurement.diff_axis_reorder:
                marker.x, marker.y, marker.z = marker.z, marker.x, marker.y

            # Flip the axis of diff
            if measurement.diff_flip_axis[0]:
                marker.x *= -1
            if measurement.diff_flip_axis[1]:
                marker.y *= -1
            if measurement.diff_flip_axis[2]:
                marker.z *= -1

            # Apply the offset
            marker.x += measurement.diff_axis_offset[0]
            marker.y += measurement.diff_axis_offset[1]
            marker.z += measurement.diff_axis_offset[2]


def calculate_base_center(
    frames: list[Frame], markers: list[MarkerEnum]
) -> dict[int, tuple[float, float, float]]:
    """
    Calculate the center of the base recording
    """
    centers = {}
    for marker_enum in markers:
        x = 0
        y = 0
        z = 0
        for frame in frames:
            if marker_enum in frame.markers:
                marker = frame.markers[marker_enum]
                x += marker.x
                y += marker.y
                z += marker.z
        centers[marker_enum] = (x / len(frames), y / len(frames), z / len(frames))
    return centers


def analyze(measurement: Measurement) -> None:
    print(f"\n\n --- Analyzing {measurement.plot_prefix} --- \n")
    base_data = QTM.from_tsv(measurement.base_recording).to_frames()
    diff_data = Frame.frames_from_csv(
        measurement.diff_recording, measurement.unit_conversion
    )

    apply_axis_transformations(diff_data, measurement)

    measurement.base_centers = calculate_base_center(base_data, measurement.markers)

    remove_average_offset(
        base_data, diff_data, measurement.markers, measurement.dominant_fps
    )

    frame_offsets(base_data, diff_data, measurement)

    remove_average_offset(
        base_data, diff_data, measurement.markers, measurement.dominant_fps
    )

    apply_diff_stretch(base_data, diff_data, measurement)

    remove_average_offset(
        base_data, diff_data, measurement.markers, measurement.dominant_fps
    )

    measurement.diff_centers = get_marker_centers(diff_data, measurement.markers)

    # plot_trajectories(base_data, diff_data, measurement, show_plot=True)

    deviations = {}
    compute_deviations_from_measurement(base_data, diff_data, measurement, deviations)

    deviations_boxplot(deviations, measurement)

    # Write the obtained results to a file
    with open(
        f"{measurement.output_prefxix}{measurement.plot_prefix}_results.txt", "w"
    ) as f:
        measurement.write(f)
        write_deviations(deviations, f)


all_markers = [MarkerEnum(i) for i in range(1, 21)]

measurements = [
    Measurement(
        base_recording="data/Qualisys/Data/multicam_asil_01.tsv",
        diff_recording="data/asil_01_front_480p_test/FULL/trajectories.csv",
        output_prefxix="data/asil_01_front_480p_test/FULL/",
        markers=all_markers,
        # diff_frame_offset=71,
        plot_prefix="",
    ),
]

if __name__ == "__main__":
    for measure in measurements:
        analyze(measure)
