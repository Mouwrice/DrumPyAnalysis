import os
from dataclasses import dataclass

from drumpy.app.main import App
from drumpy.app.video_source import Source
from drumpy.mediapipe_pose.landmarker_model import LandmarkerModel
from drumpy.mediapipe_pose.landmark_type import LandmarkType
from mediapipe.tasks.python.vision import RunningMode

"""
File to track the recordings
and output the results to a csv file
"""


@dataclass
class Recording:
    recording_path: str
    recording_name: str


recordings = [
    Recording(
        recording_path="../data/Recordings/multicam_asil_01_front_480p.mp4",
        recording_name="asil_01_front_480p_test",
    )
]


def track_recordings() -> None:
    models = [LandmarkerModel.LITE, LandmarkerModel.FULL, LandmarkerModel.HEAVY]

    for recording in recordings:
        # Create a directory with the recording name if it does not exist, in the data folder
        directory = recording.recording_name
        os.makedirs(f"../data/{directory}", exist_ok=True)

        for model in models:
            # Create a directory with the model name if it does not exist, in the recording directory
            os.makedirs(f"../data/{directory}/{model.name}", exist_ok=True)

            app = App(
                source=Source.FILE,
                file_path=recording.recording_path,
                running_mode=RunningMode.VIDEO,
                model=model,
                log_file=f"../data/{directory}/{model.name}/trajectories.csv",
                landmark_type=LandmarkType.LANDMARKS,
            )
            app.start()


if __name__ == "__main__":
    track_recordings()
