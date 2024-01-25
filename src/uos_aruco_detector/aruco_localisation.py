import argparse
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import List

import numpy as np

from .aruco_detector import ArucoDetector
from .configuration import Configuration
from .frame_decorator import Colors, FrameDecorator
from .origin_reference import OriginReference
from .tag_logger import TagLogger
from .udp_broadcast_server import UDPBroadcastServer


def detected(ids, marker_id):
    """Check if a marker with the given id is detected."""
    return np.any(ids == marker_id)


class ArucoLocalisation:
    def __init__(self, shutdown_at_end=True):
        """Initialise the ArUco localisation system."""
        # Initialisation
        self.calibrated = False
        self.initial_time_s = 0.0
        self.last_broadcast_time_s = 0.0

        print("Running ArUco localisation system")
        if shutdown_at_end:
            print("The system will shutdown at the end of the execution")
        else:
            print("WARNING: The system will NOT shutdown at the end of the execution")

        home_dir = Path.home()
        app_dir = home_dir / "uos_aruco_detector"
        log_dir = app_dir / "log"
        config_dir = app_dir / "configuration"

        if not log_dir.exists():
            log_dir.mkdir(parents=True)
        if not config_dir.exists():
            config_dir.mkdir(parents=True)

        config_file = config_dir / "configuration.yaml"
        if not config_file.exists():
            default_path = Path(__file__).parent / "configuration"
            default_configuration_file = default_path / "configuration.yaml"
            print("Copying default configuration to {}".format(config_file))
            # Copy the default configuration file to the config directory
            shutil.copy(str(default_configuration_file), str(config_file))

        self.config = Configuration(config_file)

        if self.config.usb_storage_path != "":
            self.config.usb_storage_path = Path(self.config.usb_storage_path)
            if not self.config.usb_storage_path.exists():
                print(
                    "The USB storage path {} does not exist".format(
                        self.config.usb_storage_path
                    )
                )
                print("Reverting to turn off USB storage.")
            else:
                log_dir = self.config.usb_storage_path / self.config.logging_folder
                if not log_dir.exists():
                    log_dir.mkdir(parents=True)

        now = datetime.now()
        date_time_str = now.strftime("%Y%m%d_%H%M%S")
        log_dir = log_dir / date_time_str
        if not log_dir.exists():
            log_dir.mkdir(parents=True)

        print("Logging to {}".format(log_dir))

        self.server = UDPBroadcastServer(
            self.config.udp_server_ip, self.config.udp_server_port
        )
        self.frame_decorator = FrameDecorator(
            self.config.screen_width, self.config.screen_height
        )
        self.detector = ArucoDetector(
            self.config.camera_matrix,
            self.config.camera_distortion,
            self.config.marker_size,
            self.config.frame,
        )
        self.origin = OriginReference(log_dir, self.config.frame)

        self.tag_loggers = {}
        self.stop_requested = False

        for n in self.config.tags_to_log:
            tl = TagLogger(n, f"Tag_{n}", Colors.RED, log_dir)
            self.tag_loggers[str(n)] = tl
        while not self.stop_requested:
            self.loop()

        if shutdown_at_end:
            print("Performing shutdown...")
            os.system("shutdown now -h")  # Uncomment for raspberry Pi

    def loop(self):
        """Main loop."""
        frame, corners, ids, rvecs, tvecs = self.detector.loop()
        if frame is None:
            return
        # Wait until the system is calibrated
        if not self.calibrated:
            frame = self.calibration_loop(frame, corners, ids, rvecs, tvecs)
        # When calibration has been achieved, the system is ready to start
        else:
            frame = self.detection_loop(frame, corners, ids, rvecs, tvecs)
        if not self.stop_requested:
            self.stop_requested = self.frame_decorator.show(frame)

    def draw_coordinate_system(self, frame) -> np.ndarray:
        """Draw the coordinate system."""
        frame = self.detector.drawMarkerAxes(
            frame,
            self.origin.corners,
            self.origin.rvec,
            self.origin.tvec,
            self.config.marker_size,
            self.config.frame,
        )
        return self.frame_decorator.draw_text(
            frame, self.config.frame, Colors.BLUE, (50, 100)
        )

    def get_time(self):
        """Get the current time in seconds."""
        current_time_s = datetime.now().timestamp()
        elapsed_time = current_time_s - self.initial_time_s
        return current_time_s, elapsed_time

    def reset_time(self):
        """Reset the initial time."""
        self.initial_time_s = datetime.now().timestamp()
        self.last_broadcast_time_s = self.initial_time_s

    def calibration_loop(self, frame, corners, ids, rvecs, tvecs) -> np.ndarray:
        """Detect the calibration and OK marker to set the origin.

        Parameters
        ----------
        frame : np.ndarray
            Frame to display
        corners : np.ndarray
            Detected ArUco corners
        ids : np.ndarray
            Detected ArUco ids
        rvecs : np.ndarray
            Rotation vectors
        tvecs : np.ndarray
            Translation vectors

        Returns
        -------
        np.ndarray
            Frame to display
        """
        if np.all(ids == self.config.marker.CALIBRATION):
            self.origin.set(corners[0], rvecs[0, 0, :], tvecs[0, 0, :])
            frame = self.frame_decorator.draw_text(
                frame,
                "Please present the OK tag",
                Colors.YELLOW,
            )
            frame = self.frame_decorator.draw_border(frame, Colors.YELLOW)
            frame = self.detector.draw_markers(frame, corners, ids, rvecs, tvecs)
        elif detected(ids, self.config.marker.OK) and self.origin.initialised:
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
        """Detects the aruco markers and updates the tag loggers.

        Parameters
        ----------
        frame : np.ndarray
            Frame to display
        corners : np.ndarray
            Detected ArUco corners
        ids : np.ndarray
            Detected ArUco ids
        rvecs : np.ndarray
            Rotation vectors
        tvecs : np.ndarray
            Translation vectors

        Returns
        -------
        np.ndarray
            Frame to display
        """
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

        if detected(ids, marker.BROADCAST_ALWAYS) and detected(ids, marker.OK):
            self.config.broadcast_frequency = -1
        elif detected(ids, marker.BROADCAST_FREQ_01_HZ) and detected(ids, marker.OK):
            self.config.broadcast_frequency = 0.1
        elif detected(ids, marker.BROADCAST_FREQ_02_HZ) and detected(ids, marker.OK):
            self.config.broadcast_frequency = 0.2
        elif detected(ids, marker.BROADCAST_FREQ_1_HZ) and detected(ids, marker.OK):
            self.config.broadcast_frequency = 1.0
        elif detected(ids, marker.BROADCAST_FREQ_5_HZ) and detected(ids, marker.OK):
            self.config.broadcast_frequency = 5.0
        elif detected(ids, marker.BROADCAST_NEVER) and detected(ids, marker.OK):
            self.config.broadcast_frequency = 0.0
        elif detected(ids, marker.FRAME_NED) and detected(ids, marker.OK):
            self.config.frame = "NED"
        elif detected(ids, marker.FRAME_ENU) and detected(ids, marker.OK):
            self.config.frame = "ENU"
        elif detected(ids, marker.SHUTDOWN) and detected(ids, marker.OK):
            # -- Wait one second and increase the count
            frame = frame - 100 * np.ones(frame.shape, dtype=np.uint8)
            self.frame_decorator.draw_text(frame, "Shutting down in 10 sec", Colors.RED)
            self.frame_decorator.draw_border(frame, Colors.RED)
            self.frame_decorator.show(frame)
            time.sleep(10)
            self.stop_requested = True
            self.frame_decorator.stop()
            return None

        broadcast_msg = {}
        for i, id in enumerate(ids):
            time_list, elapsed_time = self.get_time()
            # Handle platforms and broadcasting
            pos, rot = self.origin.get_relative_position(rvecs[i, 0, :], tvecs[i, 0, :])
            tl = self.tag_loggers.get(str(id[0]), None)
            if tl is None:
                print("No tag was found with ID", id)
                continue
            tl.log(time_list, elapsed_time, pos, rot, broadcast)
            broadcast_msg = tl.update_broadcast_msg(broadcast_msg)
        # Make sure to update the origin frame
        self.origin.frame = self.config.frame
        if broadcast:
            self.server.broadcast(broadcast_msg)
        return frame


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="ArUco marker detection and localisation. Given a calibration"
        + " setup this program will detect ArUco markers, log and broadcast its"
        + " positions."
    )
    parser.add_argument(
        "--no-shutdown",
        action="store_false",
        help="Don't shutdown at the end of the program",
    )
    args = parser.parse_args()
    ArucoLocalisation(args.no_shutdown)
