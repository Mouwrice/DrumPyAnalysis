from enum import Enum

from bokeh.io import output_file, show, save
from bokeh.plotting import figure

from measurement.frame import Frame
from measurement.measurement import Measurement


class Axis(Enum):
    X = "x"
    Y = "y"
    Z = "z"


def construct_line(
    frames: list[Frame], marker: int, axis: Axis
) -> tuple[list[int], list[float]]:
    """
    Extract a time, position line from the frames
    """
    line = ([], [])
    for frame in frames:
        line[0].append(frame.time_ms / 1000)
        match axis:
            case Axis.X:
                line[1].append(frame.rows[marker].x)
            case Axis.Y:
                line[1].append(frame.rows[marker].y)
            case Axis.Z:
                line[1].append(frame.rows[marker].z)
    return line


def plot_axis(
    base: list[Frame],
    diff: list[Frame],
    axis: Axis,
    base_marker: int,
    diff_marker: int,
    file_prefix: str,
    title_prefix: str,
    base_label: str,
    diff_label: str,
    show_plot: bool = False,
):
    """
    Plot the positions of the markers over time for a certain axis.
    :return:
    """
    title = f"{title_prefix}_{base_marker}_{diff_marker}_{axis}_positions"

    plot = figure(
        title=title,
        x_axis_label="Time (s)",
        y_axis_label="Position",
        sizing_mode="stretch_both",
    )

    line = construct_line(base, base_marker, axis)
    plot.line(line[0], line[1], legend_label=base_label, line_color="red")
    line = construct_line(diff, diff_marker, axis)
    plot.line(line[0], line[1], legend_label=diff_label, line_color="blue")

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
    show_plot: bool = False,
):
    for axis in Axis:
        plot_axis(
            base,
            diff,
            axis,
            base_marker,
            diff_marker,
            measurement.output_prefxix,
            measurement.plot_prefix,
            measurement.base_label,
            measurement.diff_label,
            show_plot=show_plot,
        )


def plot_trajectories(
    base: list[Frame],
    diff: list[Frame],
    measurement: Measurement,
    show_plot: bool = False,
):
    """
    Plot the trajectories of the base and diff data
    Plots the x, y and z coordinates of the markers over time using bokeh
    :param base: The base data
    :param diff: The diff data
    :param measurement: The measurement object
    :param show_plot: Opens the plot in the default browser
    """
    for key, value in measurement.mapping.items():
        plot_marker_trajectory(base, diff, measurement, key, value, show_plot)
