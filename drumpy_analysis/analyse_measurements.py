from drumpy_analysis.graphs.deviations_boxplot import deviations_boxplot
from drumpy_analysis.graphs.trajectory_lineplot import plot_trajectories
from drumpy_analysis.measurement.deviation import (
    compute_deviations_from_measurement,
    write_deviations,
    remove_average_offset,
    write_deviation_derivatives,
)
from drumpy_analysis.measurement.frame import Frame, get_marker_centers
from drumpy_analysis.measurement.measurement import Measurement
from drumpy_analysis.measurement.find_optimal_stretch import apply_diff_stretch
from drumpy_analysis.measurement.frame_offset import frame_offsets

from drumpy.tracking.marker_tracker import MarkerEnum
from drumpy_analysis.qtm.qtm_measurement import QTM
from drumpy_analysis.graphs.signal_stability import signal_stability


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
    print(f"\n\n --- Analyzing {measurement.base_recording} --- \n")
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

    plot_trajectories(base_data, diff_data, measurement, show_plot=False)

    deviations = {}
    compute_deviations_from_measurement(base_data, diff_data, measurement, deviations)

    deviations_boxplot(deviations, measurement, show_plot=False)

    signal_stability(deviations, measurement, show_plot=False)

    # Write the obtained results to a file
    with open(f"{measurement.output_prefxix}/results.txt", "w") as f:
        measurement.write(f)
        write_deviations(deviations, f)
        write_deviation_derivatives(deviations, f)


all_markers = [MarkerEnum(i) for i in range(1, 32)]

measurements = [
    Measurement(
        base_recording="data/qualisys/Data/maurice_drum_regular.tsv",
        diff_recording="data/measurements/maurice_drum_regular_world/LITE/trajectories.csv",
        output_prefxix="data/measurements/maurice_drum_regular_world/LITE/",
        markers=all_markers,
        base_frame_offset=157,
        diff_frame_offset=0,
    ),
    Measurement(
        base_recording="data/qualisys/Data/maurice_drum_regular.tsv",
        diff_recording="data/measurements/maurice_drum_regular_world/FULL/trajectories.csv",
        output_prefxix="data/measurements/maurice_drum_regular_world/FULL/",
        markers=all_markers,
        base_frame_offset=157,
        diff_frame_offset=0,
    ),
    Measurement(
        base_recording="data/qualisys/Data/maurice_drum_regular.tsv",
        diff_recording="data/measurements/maurice_drum_regular_world/HEAVY/trajectories.csv",
        output_prefxix="data/measurements/maurice_drum_regular_world/HEAVY/",
        markers=all_markers,
        base_frame_offset=157,
        diff_frame_offset=0,
    ),
    Measurement(
        base_recording="data/qualisys/Data/maurice_drum_fast.tsv",
        diff_recording="data/measurements/maurice_drum_fast_world/LITE/trajectories.csv",
        output_prefxix="data/measurements/maurice_drum_fast_world/LITE/",
        markers=all_markers,
        base_frame_offset=216,
        diff_frame_offset=0,
    ),
    Measurement(
        base_recording="data/qualisys/Data/maurice_drum_fast.tsv",
        diff_recording="data/measurements/maurice_drum_fast_world/FULL/trajectories.csv",
        output_prefxix="data/measurements/maurice_drum_fast_world/FULL/",
        markers=all_markers,
        base_frame_offset=216,
        diff_frame_offset=0,
    ),
    Measurement(
        base_recording="data/qualisys/Data/maurice_drum_fast.tsv",
        diff_recording="data/measurements/maurice_drum_fast_world/HEAVY/trajectories.csv",
        output_prefxix="data/measurements/maurice_drum_fast_world/HEAVY/",
        markers=all_markers,
        base_frame_offset=216,
        diff_frame_offset=0,
    ),
    Measurement(
        base_recording="data/qualisys/Data/maurice_drum_small.tsv",
        diff_recording="data/measurements/maurice_drum_small_world/LITE/trajectories.csv",
        output_prefxix="data/measurements/maurice_drum_small_world/LITE/",
        markers=all_markers,
        base_frame_offset=73,
        diff_frame_offset=0,
    ),
    Measurement(
        base_recording="data/qualisys/Data/maurice_drum_small.tsv",
        diff_recording="data/measurements/maurice_drum_small_world/FULL/trajectories.csv",
        output_prefxix="data/measurements/maurice_drum_small_world/FULL/",
        markers=all_markers,
        base_frame_offset=73,
        diff_frame_offset=0,
    ),
    Measurement(
        base_recording="data/qualisys/Data/maurice_drum_small.tsv",
        diff_recording="data/measurements/maurice_drum_small_world/HEAVY/trajectories.csv",
        output_prefxix="data/measurements/maurice_drum_small_world/HEAVY/",
        markers=all_markers,
        base_frame_offset=73,
        diff_frame_offset=0,
    ),
]

if __name__ == "__main__":
    for measure in measurements:
        analyze(measure)
