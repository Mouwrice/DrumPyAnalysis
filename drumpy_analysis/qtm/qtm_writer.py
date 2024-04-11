from typing import Self

import qtm_rt
from drumpy.trajectory_file import TrajectoryFile
from drumpy.tracking.landmark_type import LandmarkType


class QTMWriter:
    """
    Class to write the captured data to a CSV file.
    """

    def __init__(self: Self, path: str, time_per_frame: float = 10) -> None:
        """
        :param path:
        :param time_per_frame: Time in ms per frame
        """
        self.csv_writer = TrajectoryFile(path)
        self.time_per_frame = time_per_frame

    def on_packet(self: Self, packet: qtm_rt.QRTPacket) -> None:
        """Callback function that is called everytime a data packet arrives from QTM"""
        _, markers = packet.get_3d_markers()
        # packets at 100 Hz so time is frame number * 10 ms
        packet_time = int(packet.framenumber * self.time_per_frame)
        if self.csv_writer is not None:
            for i, marker in enumerate(markers):
                self.csv_writer.write(
                    packet.framenumber,
                    packet_time,
                    i,
                    marker.x,
                    marker.y,
                    marker.z,
                    landmark_type=LandmarkType.WORLD_LANDMARKS,
                )


async def main() -> None:
    connection = await qtm_rt.connect("127.0.0.1")
    if connection is None:
        return

    writer = QTMWriter(
        "./data/multicam_asil_01/qtm_multicam_asil_01.csv", time_per_frame=1000 / 100
    )

    await connection.stream_frames(components=["3d"], on_packet=writer.on_packet)


background_tasks = set()

if __name__ == "__main__":
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    task = loop.create_task(main())
    background_tasks.add(task)
    loop.run_forever()
    task.add_done_callback(background_tasks.discard)
