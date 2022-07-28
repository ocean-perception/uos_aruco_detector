import csv
from pathlib import Path


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
                    "Year",
                    "Month",
                    "Day",
                    "Hour",
                    "Minute",
                    "Second",
                    "Elapsed [s]",
                    "x [m]",
                    "y [m]",
                    "z [m]",
                    "Roll [deg]",
                    "Pitch [deg]",
                    "Yaw [deg]",
                    "Broadcasted 1=Yes",
                ]
            )
            file.close()

    def log(self, time_list, elapsed_time, tag_position, tag_rotation, broadcasted):
        # -- Log the detection of the tag
        with self.fname.open("a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    time_list,
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
