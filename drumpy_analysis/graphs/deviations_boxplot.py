from matplotlib import pyplot as plt

from measurement.frame import Frame
from measurement.measurement import Measurement


def row_deviation_boxplot(
    base: list[Frame],
    diff: list[Frame],
    file_prefix: str,
    title_prefix: str,
    base_marker: int,
    diff_marker: int,
    show_plot: bool = False,
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
        )
