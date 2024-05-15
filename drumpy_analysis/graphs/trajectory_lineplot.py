from enum import Enum
from typing import Self

from bokeh.io import output_file, show, save, export_svg
from bokeh.plotting import figure

from drumpy_analysis.measurement.frame import Frame
from drumpy_analysis.measurement.measurement import Measurement
from drumpy.mediapipe_pose.mediapipe_markers import MarkerEnum


class Axis(Enum):
    X = "x"
    Y = "y"
    Z = "z"

    def __str__(self: Self) -> str:
        return str(self.value)


def construct_line(
    frames: list[Frame], marker_enum: MarkerEnum, axis: Axis
) -> tuple[list[int], list[float]]:
    """
    Extract a time, position line from the frames
    """
    line = ([], [])
    for frame in frames:
        line[0].append(frame.time_ms / 1000)
        match axis:
            case Axis.X:
                line[1].append(frame.markers[marker_enum].x)
            case Axis.Y:
                line[1].append(frame.markers[marker_enum].y)
            case Axis.Z:
                line[1].append(frame.markers[marker_enum].z)
    return line


def plot_axis(
    base: list[Frame],
    diff: list[Frame],
    axis: Axis,
    marker_enum: MarkerEnum,
    file_prefix: str,
    base_label: str,
    diff_label: str,
    show_plot: bool = False,
) -> None:
    """
    Plot the positions of the markers over time for a certain axis.
    :return:
    """
    title = f"{marker_enum}_{axis}"

    # replace whitespace with underscore
    title = title.replace(" ", "_")

    plot = figure(
        title=title,
        x_axis_label="Time (s)",
        y_axis_label="Position (mm)",
        sizing_mode="stretch_both",
    )

    line = construct_line(base, marker_enum, axis)
    plot.line(line[0], line[1], legend_label=base_label, line_color="red")
    line = construct_line(diff, marker_enum, axis)
    plot.line(line[0], line[1], legend_label=diff_label, line_color="blue")

    output_file(f"{file_prefix}{title}.html")
    if show_plot:
        show(plot)
    else:
        save(plot)

    plot.output_backend = "svg"
    export_svg(plot, filename=f"{file_prefix}{title}.svg")


def plot_marker_trajectory(
    base: list[Frame],
    diff: list[Frame],
    measurement: Measurement,
    marker_enum: MarkerEnum,
    show_plot: bool = False,
) -> None:
    for axis in Axis:
        plot_axis(
            base,
            diff,
            axis,
            marker_enum,
            measurement.output_prefxix,
            measurement.base_label,
            measurement.diff_label,
            show_plot=show_plot,
        )


def plot_trajectories(
    base: list[Frame],
    diff: list[Frame],
    measurement: Measurement,
    show_plot: bool = False,
) -> None:
    """
    Plot the trajectories of the base and diff data
    Plots the x, y and z coordinates of the markers over time using bokeh
    :param base: The base data
    :param diff: The diff data
    :param measurement: The measurement object
    :param show_plot: Opens the plot in the default browser
    """
    for marker_enum in measurement.markers:
        if marker_enum not in base[0].markers or marker_enum not in diff[0].markers:
            continue

        plot_marker_trajectory(base, diff, measurement, marker_enum, show_plot)
