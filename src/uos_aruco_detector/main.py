from configuration import Configuration
from udp_broadcast_server import UDPBroadcastServer
from tag_logger import TagLogger
from frame_decorator import FrameDecorator, Colors
from aruco_detector import ArucoDetector


def main():
    # Initialisation
    calibrated = False
    config = Configuration()
    server = UDPBroadcastServer(config.udp_broadcast_port)
    frame = FrameDecorator()
    detector = ArucoDetector(config.aruco_configuration_path)

    id_list = list(range(1, 21))
    tag_loggers = []

    for n in id_list:
        tl = TagLogger(n, f"Tag_{n}", Colors.RED, config.output_folder)
        tag_loggers.append(tl)

    # Wait until the system is calibrated
    while not calibrated:
        pass

    # When calibration has been achieved, the system is ready to start
    while True:
        pass


if __name__ == "__main__":
    main()
