from matplotlib import pyplot as plt

from drumpy.mediapipe_pose.mediapipe_markers import MarkerEnum
from drumpy_analysis.measurement.deviation import Deviation
from drumpy_analysis.measurement.measurement import Measurement


def marker_signal_stability(
    deviations: list[Deviation],
    measurement: Measurement,
    marker_enum: MarkerEnum | None,
    show_plot: bool = False,
) -> None:
    """
    Plot the stability of the signal (the first derivative of the signal)
    for a certain marker
    """

    title = f"{marker_enum if marker_enum is not None else 'total'}_signal_stability"

    # Create a list of differences in deviations for each axis
    deviations_x = []
    deviations_y = []
    deviations_z = []
    for i in range(1, len(deviations)):
        deviation = deviations[i]
        previous_deviation = deviations[i - 1]
        deviations_x.append(abs(deviation.deviation_x - previous_deviation.deviation_x))
        deviations_y.append(abs(deviation.deviation_y - previous_deviation.deviation_y))
        deviations_z.append(abs(deviation.deviation_z - previous_deviation.deviation_z))

    fig, ax = plt.subplots()
    ax.boxplot([deviations_x, deviations_y, deviations_z], patch_artist=True, vert=True)

    ax.set_title(title)
    ax.set_ylabel("Deviation difference (mm)")
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


def signal_stability(
    deviations: dict[int, list[Deviation]],
    measurement: Measurement,
    show_plot: bool = False,
) -> None:
    """
    Plot the stability of the signal (the first derivative of the signal)
    """
    for marker_enum in measurement.markers:
        if marker_enum in deviations:
            marker_signal_stability(
                deviations[marker_enum], measurement, marker_enum, show_plot
            )

    marker_signal_stability(
        [deviation for deviations in deviations.values() for deviation in deviations],
        measurement,
        None,
        show_plot,
    )
