from matplotlib import pyplot as plt

from drumpy_analysis.csv_utils.csv_row import CSVRow


def row_deviations_boxplot(
    baseline: list[CSVRow],
    comparison: list[CSVRow],
    baseline_marker: int,
    comparison_marker: int,
    baseline_label: str = "qtm",
    comparison_label: str = "mediapipe",
    plot_file_prefix: str = "",
    show_plot: bool = False,
):
    """
    Plot the absolute sum of deviations of each CSVRow for a certain marker
    as a matploblib boxplot
    """

    # First calculate the average offset of the comparison to the baseline
    avg_offset_x = 0
    avg_offset_y = 0
    avg_offset_z = 0
    for i in range(len(baseline)):
        avg_offset_x += comparison[i].x - baseline[i].x
        avg_offset_y += comparison[i].y - baseline[i].y
        avg_offset_z += comparison[i].z - baseline[i].z
    avg_offset_x /= len(baseline)
    avg_offset_y /= len(baseline)
    avg_offset_z /= len(baseline)

    deviations_seperate = [[], [], []]

    # The Euclidean distance of the deviations
    deviations = []
    for i in range(len(baseline)):
        deviations_seperate[0].append(
            abs(comparison[i].x - baseline[i].x - avg_offset_x)
        )
        deviations_seperate[1].append(
            abs(comparison[i].y - baseline[i].y - avg_offset_y)
        )
        deviations_seperate[2].append(
            abs(comparison[i].z - baseline[i].z - avg_offset_z)
        )
        deviations.append(
            (
                (comparison[i].x - baseline[i].x - avg_offset_x) ** 2
                + (comparison[i].y - baseline[i].y - avg_offset_y) ** 2
                + (comparison[i].z - baseline[i].z - avg_offset_z) ** 2
            )
            ** 0.5
        )

    title = f"{plot_file_prefix}_{baseline_label}_{baseline_marker}_{comparison_label}_{comparison_marker}_deviations_seperate"

    fig, ax = plt.subplots()
    ax.boxplot(deviations_seperate, patch_artist=True, vert=True)
    ax.set_title(title)
    ax.set_ylabel("Deviation (mm)")
    ax.set_xticklabels(["x", "y", "z"])

    # increase the dpi for better quality
    fig.set_dpi(300)

    # make the plot bigger
    fig.set_size_inches(10, 5)

    # Save the plot
    plt.savefig(f"{title}.png")
    if show_plot:
        plt.show()

    # Plot the Euclidean distance of the deviations
    title = f"{plot_file_prefix}_{baseline_label}_{baseline_marker}_{comparison_label}_{comparison_marker}_deviations"
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
    plt.savefig(f"{title}.png")
    if show_plot:
        plt.show()
