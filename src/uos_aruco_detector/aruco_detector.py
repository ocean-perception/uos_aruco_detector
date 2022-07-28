import cv2
import cv2.aruco as aruco
import numpy as np


class ArucoDetector:
    def __init__(self, configuration_path):
        # --- Get the camera calibration path and parameters
        camera_matrix = np.loadtxt(
            configuration_path + "cameraMatrix_webcam.txt", delimiter=","
        )
        camera_distortion = np.loadtxt(
            configuration_path + "cameraDistortion_webcam.txt", delimiter=","
        )

        # --- Define the aruco dictionary
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_100)
        self.parameters = aruco.DetectorParameters_create()

        # --- Capture the videocamera (this may also be a video or a picture)
        self.cap = cv2.VideoCapture(0)

        # -- Set the camera size as the one it was calibrated with
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    def loop(self):
        # -- Read the frame
        _, frame = self.cap.read()

        # -- Convert to gray scale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # -- Find the aruco markers
        corners, ids, rejectedImgPoints = aruco.detectMarkers(
            gray, self.aruco_dict, self.parameters
        )

        rvecs = []
        tvecs = []

        # -- Estimate the pose of the aruco markers
        if ids is not None and ids.size > 0:
            # -- Get the corners of the aruco markers
            corners = aruco.refineDetectedMarkers(gray, corners, rejectedImgPoints)
            # -- Estimate the pose of the aruco markers
            rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(
                corners, 0.05, self.camera_matrix, self.camera_distortion
            )
        return frame, corners, ids, rvecs, tvecs

    def draw_markers(self, frame, corners, ids, rvecs, tvecs):
        # -- Draw detected aruco markers
        aruco.drawDetectedMarkers(frame, corners, ids)
        # -- Draw detected aruco markers axis
        self.draw_axes(frame, rvecs, tvecs)

    def draw_axes(self, frame, rvecs, tvecs):
        # -- Draw axis for the aruco markers
        aruco.drawAxis(
            frame, self.camera_matrix, self.camera_distortion, rvecs, tvecs, 0.1
        )
