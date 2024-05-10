from matplotlib import pyplot as plt

from drumpy_analysis.measurement.deviation import Deviation
from drumpy_analysis.measurement.measurement import Measurement

from drumpy.mediapipe_pose.mediapipe_markers import MarkerEnum


def row_deviation_boxplot(
    deviations: list[Deviation],
    measurement: Measurement,
    marker_enum: MarkerEnum | None,
    show_plot: bool = False,
) -> None:
    """
    Plots the deviations of a certain marker as a matplotlib boxplot
    """

    title = f"{marker_enum if marker_enum is not None else 'total'}_deviations_seperate"

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

    plt.close(fig)

    # Plot the Euclidean distance of the deviations
    title = f"{marker_enum if marker_enum is not None else 'total'}_deviations"
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

    plt.close(fig)


def deviations_boxplot(
    deviations: dict[int, list[Deviation]],
    measurement: Measurement,
    show_plot: bool = False,
) -> None:
    """
    Plot the deviations of all markers
    """
    for marker_enum in measurement.markers:
        if marker_enum in deviations:
            row_deviation_boxplot(
                deviations[marker_enum],
                measurement,
                marker_enum,
                show_plot=show_plot,
            )

    # total deviations
    row_deviation_boxplot(
        [
            deviation
            for deviations_list in deviations.values()
            for deviation in deviations_list
        ],
        measurement,
        None,
        show_plot=show_plot,
    )
