from matplotlib import pyplot as plt

from drumpy_analysis.measurement.deviation import Deviation
from drumpy_analysis.measurement.measurement import Measurement


def row_deviation_boxplot(
    deviations: list[Deviation],
    measurement: Measurement,
    base_marker: int,
    diff_marker: int,
    show_plot: bool = False,
):
    """
    Plot the absolute sum of deviations of each frame for a certain marker
    as a matploblib boxplot
    """

    title = f"{measurement.plot_prefix}_{base_marker}_{diff_marker}_deviations_seperate"

    # Create a list of absolute deviations for each axis
    absolute_deviations = [[], [], []]
    euclidean_deviations = []
    for deviation in deviations:
        absolute_deviations[0].append(deviation.deviation_x)
        absolute_deviations[1].append(deviation.deviation_y)
        absolute_deviations[2].append(deviation.deviation_z)
        euclidean_deviations.append(deviation.euclidean_distance)

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
    plt.savefig(f"{measurement.output_prefxix}{title}.png")
    if show_plot:
        plt.show()

    # Plot the Euclidean distance of the deviations
    title = f"{measurement.plot_prefix}_{base_marker}_{diff_marker}_deviations"
    fig, ax = plt.subplots()
    ax.boxplot(euclidean_deviations, patch_artist=True, vert=True)
    ax.set_title(title)
    ax.set_ylabel("Deviation (mm)")
    ax.set_xticklabels(["euclidean distance based"])

    # increase the dpi for better quality
    fig.set_dpi(300)

    # make the plot bigger
    fig.set_size_inches(10, 5)

    # Save the plot
    plt.savefig(f"{measurement.output_prefxix}{title}.png")
    if show_plot:
        plt.show()


def deviations_boxplot(
    deviations: dict[int, list[Deviation]],
    measurement: Measurement,
    show_plot: bool = False,
):
    """
    Plot the absolute sum of deviations of each frame for a certain marker
    as a matploblib boxplot
    """
    for base_marker, diff_marker in measurement.mapping.items():
        row_deviation_boxplot(
            deviations[diff_marker],
            measurement,
            base_marker,
            diff_marker,
            show_plot=show_plot,
        )
