from bokeh.io import output_file, show, save
from bokeh.plotting import figure

from drumpy_analysis.csv_utils.frame import Frame
from measurement import Measurement


def get_closest_frame_index(frames: list[Frame], frame: int) -> int:
    """
    Get the index of the frame with the closest frame number
    :param frames:
    :param frame:
    :return:
    """
    return min(range(len(frames)), key=lambda i: abs(frames[i].frame - frame))


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
        elif base_time > diff_time:
            diff_idx += 1
            diff_frame = diff_next_frame
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


def apply_offset_scale_rotation(
    frames: list[Frame], offset: float, scale: float, rotation: float
):
    """
    Apply offset, scale and rotation to the frames
    """
    for frame in frames:
        for row in frame.rows:
            row.x = (row.x + offset) * scale
            row.y = (row.y + offset) * scale
            row.z = (row.z + offset) * scale

    if rotation != 0:
        raise NotImplementedError("Rotation not implemented yet")


def plot_axis(
    axis1: list[float],
    axis2: list[float],
    axis: str,
    marker1: int,
    marker2: int,
    file_prefix: str,
    title_prefix: str,
    label1: str,
    label2: str,
    show_plot: bool = False,
):
    """
    Plot the positions of the markers over time for a certain axis.
    Normalizes the values between 0 and 1
    :return:
    """

    # Remove the average offset from the data
    avg_offset = 0
    for i in range(len(axis1)):
        avg_offset += axis2[i] - axis1[i]
    avg_offset /= len(axis1)

    for i in range(len(axis1)):
        axis2[i] -= avg_offset

    title = f"{title_prefix}_{marker1}_{marker2}_{axis}_positions"

    plot = figure(
        title=title,
        x_axis_label="Frame",
        y_axis_label="Position",
        sizing_mode="stretch_both",
    )
    plot.line(list(range(len(axis1))), axis1, legend_label=label1, line_color="red")
    plot.line(list(range(len(axis2))), axis2, legend_label=label2, line_color="blue")

    output_file(f"{file_prefix}{title}.html")
    if show_plot:
        show(plot)
    else:
        save(plot)


def plot_marker_trajectory(
    base: list[Frame],
    diff: list[Frame],
    measurement: Measurement,
    base_marker: int,
    diff_marker: int,
):
    """
    Plot the trajectory of a marker over time using bokeh
    """
    base_x = []
    base_y = []
    base_z = []
    diff_x = []
    diff_y = []
    diff_z = []

    for base_frame, diff_frame in zip(base, diff):
        base_row = base_frame.rows[base_marker]
        diff_row = diff_frame.rows[diff_marker]
        base_x.append(base_row.x)
        base_y.append(base_row.y)
        base_z.append(base_row.z)
        diff_x.append(diff_row.x)
        diff_y.append(diff_row.y)
        diff_z.append(diff_row.z)

    plot_axis(
        base_x,
        diff_x,
        "x",
        base_marker,
        diff_marker,
        measurement.output_prefxix,
        measurement.plot_prefix,
        measurement.base_label,
        measurement.diff_label,
    )

    plot_axis(
        base_y,
        diff_y,
        "y",
        base_marker,
        diff_marker,
        measurement.output_prefxix,
        measurement.plot_prefix,
        measurement.base_label,
        measurement.diff_label,
    )

    plot_axis(
        base_z,
        diff_z,
        "z",
        base_marker,
        diff_marker,
        measurement.output_prefxix,
        measurement.plot_prefix,
        measurement.base_label,
        measurement.diff_label,
    )


def plot_trajectories(
    base: list[Frame],
    diff: list[Frame],
    measurement: Measurement,
    mapping: dict[int, int],
):
    """
    Plot the trajectories of the base and diff data
    Plots the x, y and z coordinates of the markers over time using bokeh
    :param base: The base data
    :param diff: The diff data
    :param measurement: The measurement object
    :param mapping: Used to map the markers from the base to the diff data
    """
    for key, value in mapping.items():
        plot_marker_trajectory(base, diff, measurement, key, value)


def plot_measurement(measurement: Measurement):
    """
    Plots the measurement
    """
    base_data = Frame.frames_from_csv(measurement.base_recording)
    diff_data = Frame.frames_from_csv(
        measurement.diff_recording, measurement.unit_conversion
    )

    base_arranged, diff_arranged = arrange_measurement_data(
        base_data,
        diff_data,
        measurement.base_frame_offset,
        measurement.diff_frame_offset,
    )

    apply_offset_scale_rotation(
        diff_arranged,
        measurement.axis_offset,
        measurement.axis_scale,
        measurement.axis_rotation,
    )

    plot_trajectories(base_arranged, diff_arranged, measurement, qtm_to_mediapipe)


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
        base_frame_offset=0,
        diff_frame_offset=0,
        output_prefxix="data/multicam_asil_01/",
        axis_offset=0,
        axis_scale=1,
        axis_rotation=0,
        plot_prefix="multicam_asil_01_front_LITE_async",
        base_label="QTM",
        diff_label="Mediapipe",
    ),
]

if __name__ == "__main__":
    for measure in measurements:
        plot_measurement(measure)
