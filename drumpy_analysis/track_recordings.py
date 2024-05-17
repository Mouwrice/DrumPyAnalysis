import os
from dataclasses import dataclass

from drumpy.app.main import App
from drumpy.app.video_source import Source
from drumpy.mediapipe_pose.landmarker_model import LandmarkerModel
from drumpy.mediapipe_pose.landmark_type import LandmarkType
from mediapipe.tasks.python import BaseOptions
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
        recording_path="../data/recordings/maurice_drum_fast.mov",
        recording_name="maurice_drum_fast_processed",
    ),
]


def track_recordings() -> None:
    models = [LandmarkerModel.LITE]  # , LandmarkerModel.FULL, LandmarkerModel.HEAVY]

    for recording in recordings:
        # Create a directory with the recording name if it does not exist, in the data folder
        directory = recording.recording_name
        os.makedirs(f"../data/measurements/{directory}", exist_ok=True)

        for model in models:
            # Create a directory with the model name if it does not exist, in the recording directory
            os.makedirs(f"../data/measurements/{directory}/{model.name}", exist_ok=True)

            app = App(
                source=Source.FILE,
                file_path=recording.recording_path,
                running_mode=RunningMode.VIDEO,
                delegate=BaseOptions.Delegate.GPU,
                model=model,
                log_file=f"../data/measurements/{directory}/{model.name}/trajectories.csv",
                landmark_type=LandmarkType.LANDMARKS,
                disable_drum=True,
            )
            app.start()


if __name__ == "__main__":
    track_recordings()
