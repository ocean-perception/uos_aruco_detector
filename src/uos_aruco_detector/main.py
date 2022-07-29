from configuration import Configuration
from udp_broadcast_server import UDPBroadcastServer
from tag_logger import TagLogger
from frame_decorator import FrameDecorator, Colors
from aruco_detector import ArucoDetector
from origin_reference import OriginReference
import numpy as np


def main():
    # Initialisation
    calibrated = False
    config = Configuration()
    server = UDPBroadcastServer(config.udp_broadcast_port)
    frame_decorator = FrameDecorator()
    detector = ArucoDetector(config.aruco_configuration_path)
    origin = OriginReference(config.output_folder)

    id_list = list(range(1, 21))
    tag_loggers = []

    for n in id_list:
        tl = TagLogger(n, f"Tag_{n}", Colors.RED, config.output_folder)
        tag_loggers.append(tl)

    # Wait until the system is calibrated
    while not calibrated:
        frame, corners, ids, rvecs, tvecs = detector.loop()
        if np.all(ids == config.marker.calibration):
            origin.set(rvecs[0], tvecs[0])
            frame_decorator.draw_text(
                frame,
                "Please present the OK tag",
                Colors.YELLOW,
            )
            frame_decorator.draw_rectangle(frame, Colors.YELLOW)
        elif np.any(ids == Oconfig.marker.ok) and origin.initialised:
            calibrated = True
        frame_decorator.show(frame)

    # When calibration has been achieved, the system is ready to start
    while True:
        pass


if __name__ == "__main__":
    main()
