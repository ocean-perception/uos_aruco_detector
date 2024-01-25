from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Marker:
    OK: int = -1
    CALIBRATION: int = -1
    BROADCAST_NEVER: int = -1
    BROADCAST_FREQ_01_HZ: int = -1
    BROADCAST_FREQ_02_HZ: int = -1
    BROADCAST_FREQ_1_HZ: int = -1
    BROADCAST_FREQ_5_HZ: int = -1
    BROADCAST_ALWAYS: int = -1
    FRAME_NED: int = -1
    FRAME_ENU: int = -1
    SHUTDOWN: int = -1
    PLATFORM_1: int = -1
    PLATFORM_2: int = -1
    PLATFORM_3: int = -1
    PLATFORM_4: int = -1
    PLATFORM_5: int = -1


class Configuration:
    def __init__(self, filename):
        if not Path(filename).exists():
            raise FileNotFoundError(f"Configuration file {filename} not found")
        self.filename = filename
        self.marker = Marker()
        self.load()

    def load(self):
        f = self.filename.open("r")
        config = yaml.safe_load(f)
        # -- Define path where all code is stored
        self.logging_folder = config["logging_folder"]
        self.usb_storage_path = config["usb_storage_path"]
        # --- Define Tags
        self.marker_size = float(config["defaults"]["marker_size"])  # [m]
        self.marker.OK = int(config["markers"]["OK"])
        self.marker.CALIBRATION = int(config["markers"]["CALIBRATION"])
        self.marker.BROADCAST_NEVER = int(config["markers"]["BROADCAST_NEVER"])
        self.marker.BROADCAST_FREQ_01_HZ = int(
            config["markers"]["BROADCAST_FREQ_01_HZ"]
        )
        self.marker.BROADCAST_FREQ_02_HZ = int(
            config["markers"]["BROADCAST_FREQ_02_HZ"]
        )
        self.marker.BROADCAST_FREQ_1_HZ = int(config["markers"]["BROADCAST_FREQ_1_HZ"])
        self.marker.BROADCAST_FREQ_5_HZ = int(config["markers"]["BROADCAST_FREQ_5_HZ"])
        self.marker.BROADCAST_ALWAYS = int(config["markers"]["BROADCAST_ALWAYS"])
        self.marker.FRAME_NED = int(config["markers"]["FRAME_NED"])
        self.marker.FRAME_ENU = int(config["markers"]["FRAME_ENU"])
        self.marker.SHUTDOWN = int(config["markers"]["SHUTDOWN"])

        self.udp_server_port = int(config["udp_server"]["port"])
        self.udp_server_ip = config["udp_server"]["ip"]

        self.camera_matrix = config["camera"]["matrix"]
        self.camera_distortion = config["camera"]["distortion"]

        self.screen_width = config["defaults"].get("screen_width", 1920)
        self.screen_height = config["defaults"].get("screen_height", 1920)

        self.broadcast_frequency = float(
            config["defaults"]["broadcast_frequency"]  # [Hz]
        )
        self.frame = config["defaults"]["frame"]
        self.tags_to_log = config["defaults"]["tags_to_log"]
