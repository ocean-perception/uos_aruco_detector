import csv
from pathlib import Path

from .udp_broadcast_server import (
    UDPBroadcastServer,
)


class TagLogger:
    def __init__(self, tag_id, tag_name, tag_color, log_dir):
        self.tag_id = tag_id
        self.tag_name = tag_name
        self.tag_color = tag_color
        self.fname = Path(log_dir) / f"{tag_id}_{tag_name}.csv"
        with self.fname.open("w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "epoch [s]",
                    "elapsed [s]",
                    "x [m]",
                    "y [m]",
                    "z [m]",
                    "roll [deg]",
                    "pitch [deg]",
                    "yaw [deg]",
                    "broadcasted 1=yes",
                ]
            )
            file.close()

    def broadcast(self, udp_socket_server: UDPBroadcastServer):
        # -- Broadcast the tag position and rotation
        udp_socket_server.broadcast(
            f"{self.tag_id},{self.current_time},{self.elapsed_time},{self.tag_position},{self.tag_rotation}"
        )

    def log(self, current_time, elapsed_time, tag_position, tag_rotation, broadcasted):
        self.current_time = current_time
        self.elapsed_time = elapsed_time
        self.tag_position = tag_position
        self.tag_rotation = tag_rotation
        # -- Log the detection of the tag
        with self.fname.open("a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    current_time,
                    elapsed_time,
                    tag_position[0],
                    tag_position[1],
                    tag_position[2],
                    tag_rotation[0],
                    tag_rotation[1],
                    tag_rotation[2],
                    broadcasted,
                ]
            )
            file.close()
