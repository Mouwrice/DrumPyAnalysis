from typing import TextIO

import pandas as pd
from matplotlib import pyplot as plt

from measurement.frame import Frame
from measurement.measurement import Measurement


def get_box_plot_data(labels, bp):
    rows_list = []

    for i in range(len(labels)):
        dict1 = {
            "label": labels[i],
            "lower_whisker": bp["whiskers"][i * 2].get_ydata()[1],
            "lower_quartile": bp["boxes"][i].get_ydata()[1],
            "median": bp["medians"][i].get_ydata()[1],
            "upper_quartile": bp["boxes"][i].get_ydata()[2],
            "upper_whisker": bp["whiskers"][(i * 2) + 1].get_ydata()[1],
        }
        rows_list.append(dict1)

    return pd.DataFrame(rows_list)


def row_deviation_boxplot(
    base: list[Frame],
    diff: list[Frame],
    file_prefix: str,
    title_prefix: str,
    base_marker: int,
    diff_marker: int,
    show_plot: bool = False,
    file: TextIO = None,
):
    """
    Plot the absolute sum of deviations of each frame for a certain marker
    as a matploblib boxplot
    """

    absolute_deviations = ([], [], [])
    # The Euclidean distance of the deviations
    deviations = []
    for i in range(len(base)):
        base_row = base[i].rows[base_marker]
        diff_row = diff[i].rows[diff_marker]

        absolute_deviations[0].append(abs(diff_row.x - base_row.x))
        absolute_deviations[1].append(abs(diff_row.y - base_row.y))
        absolute_deviations[2].append(abs(diff_row.z - base_row.z))
        deviations.append(
            (
                (diff_row.x - base_row.x) ** 2
                + (diff_row.y - base_row.y) ** 2
                + (diff_row.z - base_row.z) ** 2
            )
            ** 0.5
        )

    if file is not None:
        data = pd.DataFrame(
            {
                "x": absolute_deviations[0],
                "y": absolute_deviations[1],
                "z": absolute_deviations[2],
                "Euclidean distance": deviations,
            }
        ).describe()
        file.write(f"{title_prefix}_{base_marker}_{diff_marker}\n")
        file.write(data.to_string())
        file.write("\n\n")

    title = f"{title_prefix}_{base_marker}_{diff_marker}_deviations_seperate"

    fig, ax = plt.subplots()
    ax.boxplot(absolute_deviations, patch_artist=True, vert=True)

    ax.set_title(title)
    ax.set_ylabel("Deviation (mm)")
    ax.set_xticklabels(["x", "y", "z"])

    # increase the dpi for better quality
    fig.set_dpi(300)

    # make the plot bigger
    fig.set_size_inches(10, 5)

    # Save the plot
    plt.savefig(f"{file_prefix}{title}.png")
    if show_plot:
        plt.show()

    # Plot the Euclidean distance of the deviations
    title = f"{title_prefix}_{base_marker}_{diff_marker}_deviations"
    fig, ax = plt.subplots()
    ax.boxplot(deviations, patch_artist=True, vert=True)
    ax.set_title(title)
    ax.set_ylabel("Deviation (mm)")
    ax.set_xticklabels(["euclidean distance based"])

    # increase the dpi for better quality
    fig.set_dpi(300)

    # make the plot bigger
    fig.set_size_inches(10, 5)

    # Save the plot
    plt.savefig(f"{file_prefix}{title}.png")
    if show_plot:
        plt.show()


def deviations_boxplot(
    base: list[Frame],
    diff: list[Frame],
    measurement: Measurement,
    file: TextIO = None,
):
    """
    Plot the absolute sum of deviations of each frame for a certain marker
    as a matploblib boxplot
    """
    for base_marker, diff_marker in measurement.mapping.items():
        row_deviation_boxplot(
            base,
            diff,
            measurement.output_prefxix,
            measurement.plot_prefix,
            base_marker,
            diff_marker,
            file=file,
        )
