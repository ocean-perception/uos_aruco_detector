from .configuration import Configuration
from .udp_broadcast_server import UDPBroadcastServer
from .tag_logger import TagLogger
from .frame_decorator import FrameDecorator, Colors
from .aruco_detector import ArucoDetector
from .origin_reference import OriginReference
import numpy as np
from datetime import datetime
from pathlib import Path
import os
import time
import shutil


def detected(ids, marker_id):
    return marker_id in ids


class ArucoLocalisation:
    def __init__(self):
        # Initialisation
        self.calibrated = False
        self.initial_time_s = 0.0
        self.last_broadcast_time_s = 0.0

        home_dir = Path.home()
        app_dir = home_dir / "uos_aruco_detector"
        log_dir = app_dir / "log"
        config_dir = app_dir / "config"

        if not log_dir.exists():
            log_dir.mkdir(parents=True)
        if not config_dir.exists():
            config_dir.mkdir(parents=True)

        config_file = config_dir / "configuration.yaml"
        if not config_file.exists():
            default_path = Path(__file__).resolve().parents[2] / "config"
            default_configuration_file = default_path / "configuration.yaml"
            print("Copying default configuration to {}".format(config_file))
            # Copy the default configuration file to the config directory
            shutil.copy(str(default_configuration_file), str(config_file))

        self.config = Configuration(config_file)
        self.server = UDPBroadcastServer(
            self.config.udp_server_ip, self.config.udp_server_port
        )
        self.frame_decorator = FrameDecorator()
        self.detector = ArucoDetector(
            self.config.camera_matrix, self.config.camera_distortion
        )
        self.origin = OriginReference(config_dir)

        self.tag_loggers = []
        self.stop_requested = False

        self.config.logging_folder = Path(self.config.logging_folder)
        if not self.config.logging_folder.exists():
            self.config.logging_folder.mkdir()

        id_list = list(range(1, 6))
        for n in id_list:
            tl = TagLogger(n, f"Tag_{n}", Colors.RED, self.config.logging_folder)
            self.tag_loggers.append(tl)
        while not self.stop_requested:
            self.loop()

        print("Performing shutdown...")
        # os.system("shutdown now h-")  # Uncomment for raspberry Pi

    def loop(self):
        frame, corners, ids, rvecs, tvecs = self.detector.loop()
        # Wait until the system is calibrated
        if not self.calibrated:
            frame = self.calibration_loop(frame, ids, rvecs, tvecs)
        # When calibration has been achieved, the system is ready to start
        else:
            frame = self.detection_loop(frame, corners, ids, rvecs, tvecs)
        if not self.stop_requested:
            self.stop_requested = self.frame_decorator.show(frame)

    def draw_coordinate_system(self, frame) -> np.ndarray:
        frame = self.detector.draw_axes(frame, self.origin.rvec, self.origin.tvec)
        return self.frame_decorator.draw_text(
            frame, self.config.frame, Colors.BLUE, (50, 100)
        )

    def get_time(self):
        # -- Obtain current time and format it
        current_time_s = datetime.now().timestamp()
        elapsed_time = current_time_s - self.initial_time_s
        return current_time_s, elapsed_time

    def reset_time(self):
        self.initial_time_s = datetime.now().timestamp()
        self.last_broadcast_time_s = self.initial_time_s

    def calibration_loop(self, frame, ids, rvecs, tvecs) -> np.ndarray:
        if np.all(ids == self.config.marker.CALIBRATION):
            self.origin.set(rvecs[0, 0, :], tvecs[0, 0, :])
            frame = self.frame_decorator.draw_text(
                frame,
                "Please present the OK tag",
                Colors.YELLOW,
            )
            frame = self.frame_decorator.draw_border(frame, Colors.YELLOW)
        elif np.any(ids == self.config.marker.OK) and self.origin.initialised:
            self.calibrated = True
            self.reset_time()
        else:
            self.frame_decorator.draw_text(
                frame,
                "Please present the calibration tag",
                Colors.YELLOW,
            )
            frame = self.frame_decorator.draw_border(frame, Colors.RED)
        return frame

    def detection_loop(self, frame, corners, ids, rvecs, tvecs) -> np.ndarray:
        frame = self.draw_coordinate_system(frame)
        frame = self.frame_decorator.draw_border(frame, Colors.GREEN)
        frame = self.detector.draw_markers(frame, corners, ids, rvecs, tvecs)

        # Shorten name
        marker = self.config.marker

        # Handle broadcasting frequency
        broadcast = False
        current_time_s = datetime.now().timestamp()
        broadcast_interval = 1.0 / self.config.broadcast_frequency
        if current_time_s - self.last_broadcast_time_s > broadcast_interval:
            broadcast = True
            self.last_broadcast_time_s = current_time_s

        if ids is None:
            return frame

        if np.any(ids == marker.BROADCAST_ALWAYS) and np.any(ids == marker.OK):
            self.config.broadcast_frequency = -1
        elif np.any(ids == marker.BROADCAST_FREQ_1_HZ) and np.any(ids == marker.OK):
            self.config.broadcast_frequency = 1.0
        elif np.any(ids == marker.BROADCAST_FREQ_2_HZ) and np.any(ids == marker.OK):
            self.config.broadcast_frequency = 2.0
        elif np.any(ids == marker.BROADCAST_FREQ_5_HZ) and np.any(ids == marker.OK):
            self.config.broadcast_frequency = 5.0
        elif np.any(ids == marker.BROADCAST_FREQ_10_HZ) and np.any(ids == marker.OK):
            self.config.broadcast_frequency = 10.0
        elif np.any(ids == marker.BROADCAST_NEVER) and np.any(ids == marker.OK):
            self.config.broadcast_frequency = 0.0
        elif np.any(ids == marker.FRAME_NED) and np.any(ids == marker.OK):
            self.config.frame = "NED"
        elif np.any(ids == marker.FRAME_ENU) and np.any(ids == marker.OK):
            self.config.frame = "ENU"
        elif np.any(ids == marker.SHUTDOWN) and np.any(ids == marker.OK):
            # -- Wait one second and increase the count
            frame = frame - 100 * np.ones(frame.shape, dtype=np.uint8)
            self.frame_decorator.draw_text(frame, "Shutting down in 10 sec", Colors.RED)
            self.frame_decorator.draw_border(frame, Colors.RED)
            self.frame_decorator.show(frame)
            time.sleep(10)
            self.stop_requested = True
            self.frame_decorator.stop()
            return None

        for i, id in enumerate(ids):
            time_list, elapsed_time = self.get_time()
            # Handle platforms and broadcasting
            if detected(id, marker.PLATFORM_1):
                pos, rot = self.origin.get_relative_position(
                    rvecs[i, 0, :], tvecs[i, 0, :]
                )
                self.tag_loggers[0].log(time_list, elapsed_time, pos, rot, broadcast)
                if broadcast:
                    self.tag_loggers[0].broadcast(self.server)
            elif detected(id, marker.PLATFORM_2):
                pos, rot = self.origin.get_relative_position(
                    rvecs[i, 0, :], tvecs[i, 0, :]
                )
                self.tag_loggers[1].log(time_list, elapsed_time, pos, rot, broadcast)
                if broadcast:
                    self.tag_loggers[1].broadcast(self.server)
            elif detected(id, marker.PLATFORM_3):
                pos, rot = self.origin.get_relative_position(
                    rvecs[i, 0, :], tvecs[i, 0, :]
                )
                self.tag_loggers[2].log(time_list, elapsed_time, pos, rot, broadcast)
                if broadcast:
                    self.tag_loggers[2].broadcast(self.server)
            elif detected(id, marker.PLATFORM_4):
                pos, rot = self.origin.get_relative_position(
                    rvecs[i, 0, :], tvecs[i, 0, :]
                )
                self.tag_loggers[3].log(time_list, elapsed_time, pos, rot, broadcast)
                if broadcast:
                    self.tag_loggers[3].broadcast(self.server)
            elif detected(id, marker.PLATFORM_5):
                pos, rot = self.origin.get_relative_position(
                    rvecs[i, 0, :], tvecs[i, 0, :]
                )
                self.tag_loggers[4].log(time_list, elapsed_time, pos, rot, broadcast)
                if broadcast:
                    self.tag_loggers[4].broadcast(self.server)
        return frame


def main():
    ArucoLocalisation()
