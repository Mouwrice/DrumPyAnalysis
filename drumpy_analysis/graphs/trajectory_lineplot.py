from bokeh.io import output_file, show, save
from bokeh.plotting import figure

from measurement.frame import Frame
from measurement.measurement import Measurement


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
    :return:
    """
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
    show_plot: bool = False,
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
        show_plot=show_plot,
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
        show_plot=show_plot,
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
