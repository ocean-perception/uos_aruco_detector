from configuration import Configuration
from udp_broadcast_server import UDPBroadcastServer
from tag_logger import TagLogger
from frame_decorator import FrameDecorator, Colors
from aruco_detector import ArucoDetector
from origin_reference import OriginReference
import numpy as np


class ArucoLocalisation:
    def __init__(self):
        # Initialisation
        self.calibrated = False
        self.config = Configuration()
        self.server = UDPBroadcastServer(config.udp_broadcast_port)
        self.frame_decorator = FrameDecorator()
        self.detector = ArucoDetector(config.aruco_configuration_path)
        self.origin = OriginReference(config.output_folder)

        self.tag_loggers = []
        self.stop_requested = False

        id_list = list(range(1, 21))
        for n in id_list:
            tl = TagLogger(n, f"Tag_{n}", Colors.RED, self.config.output_folder)
            self.tag_loggers.append(tl)
        while not self.stop_requested:
            self.loop()

    def loop(self):
        frame, corners, ids, rvecs, tvecs = self.detector.loop()
        # Wait until the system is calibrated
        if not self.calibrated:
            self.calibration_loop(frame, ids, rvecs, tvecs)
        # When calibration has been achieved, the system is ready to start
        else:
            self.draw_coordinate_system(frame)
            self.detection_loop(frame, corners, ids, rvecs, tvecs)
        self.stop_requested = self.frame_decorator.show(frame)

    def draw_coordinate_system(self, frame):
        self.frame_decorator.draw_text(
            frame, self.config.coordinate_system, Colors.BLUE, (50, 100)
        )

    def calibration_loop(self, frame, ids, rvecs, tvecs):
        if np.all(ids == self.config.marker.calibration):
            self.origin.set(rvecs[0], tvecs[0])
            self.frame_decorator.draw_text(
                frame,
                "Please present the OK tag",
                Colors.YELLOW,
            )
            self.frame_decorator.draw_rectangle(frame, Colors.YELLOW)
        elif np.any(ids == self.config.marker.ok) and self.origin.initialised:
            self.calibrated = True
        else:
            self.frame_decorator.draw_text(
                frame,
                "Please present the calibration tag",
                Colors.YELLOW,
            )
            self.frame_decorator.draw_rectangle(frame, Colors.RED)

    def detection_loop(self, frame):
        pass

def main():
    


if __name__ == "__main__":
    main()
