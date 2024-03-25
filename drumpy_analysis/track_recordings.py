from drumpy.app.main import App
from drumpy.app.video_source import Source
from drumpy.landmarkermodel import LandmarkerModel

"""
File to track the recordings
and output the results to a csv file
"""


def track_redcordings():
    recordings = [
        "../recordings/multicam_asil_01_front.mkv",
        # "../recordings/multicam_asil_01_left.mkv",
        # "../recordings/multicam_asil_01_right.mkv",
        # "../recordings/multicam_asil_02_front.mkv",
        # "../recordings/multicam_asil_02_left.mkv",
        # "../recordings/multicam_asil_02_right.mkv",
        # "../recordings/multicam_asil_03_front.mkv",
        # "../recordings/multicam_asil_03_left.mkv",
        # "../recordings/multicam_asil_03_right.mkv",
        # "../recordings/multicam_ms_01_front.mkv",
        # "../recordings/multicam_ms_01_left.mkv",
        # "../recordings/multicam_ms_01_right.mkv",
        # "../recordings/multicam_ms_02_front.mkv",
        # "../recordings/multicam_ms_02_left.mkv",
        # "../recordings/multicam_ms_02_right.mkv",
    ]

    models = [LandmarkerModel.LITE, LandmarkerModel.FULL, LandmarkerModel.HEAVY]

    for recording in recordings:
        for model in models:
            file_name = recording.split("/")[-1].replace(".mkv", "")
            # omit everything after the second underscore
            split_name = file_name.split("_")
            directory = f"{'_'.join(split_name[1:3])}/{split_name[3]}"
            print(f"Recording: {recording}, Model: {model}, Async")

            app = App(
                source=Source.FILE,
                file_path=recording,
                live_stream=False,
                model=model,
                log_file=f"./data/{directory}/{model.name}.csv",
            )
            app.start()


if __name__ == "__main__":
    track_redcordings()
