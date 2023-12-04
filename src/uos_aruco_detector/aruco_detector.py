import cv2
import cv2.aruco as aruco
import numpy as np
from scipy.spatial.transform import Rotation


class ArucoDetector:
    def __init__(self, camera_matrix, camera_distortion, marker_size, frame_type):
        # --- Get the camera calibration path and parameters
        self.camera_matrix = np.array(camera_matrix)
        self.camera_distortion = np.array(camera_distortion)
        self.marker_size = marker_size
        self.frame_type = frame_type
        # --- Define the aruco dictionary
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_100)
        self.parameters = aruco.DetectorParameters_create()

        # --- Capture the videocamera (this may also be a video or a picture)
        self.cap = cv2.VideoCapture(0)

    def loop(self):
        # -- Read the frame
        ret, frame = self.cap.read()
        # Check if frame is not empty
        if not ret:
            print("Could not grab a frame")
            return None, None, None, None, None

        # -- Convert to gray scale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # -- Find the aruco markers
        corners, ids, _ = aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.parameters
        )
        rvecs = []
        tvecs = []
        # -- Estimate the pose of the aruco markers
        if ids is not None and ids.size > 0:
            # -- Get the corners of the aruco markers
            # corners = aruco.refineDetectedMarkers(gray, corners, rejectedImgPoints)
            # -- Estimate the pose of the aruco markers
            rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(
                corners, self.marker_size, self.camera_matrix, self.camera_distortion
            )
        return frame, corners, ids, rvecs, tvecs

    def draw_markers(self, frame, corners, ids, rvecs, tvecs) -> np.ndarray:
        if ids is None:
            return frame
        # -- Draw detected aruco markers
        aruco.drawDetectedMarkers(frame, corners, ids)
        # -- Draw detected aruco markers axis
        for i in range(len(ids)):
            frame = self.drawMarkerAxes(
                frame,
                corners[i],
                rvecs[i, 0, :],
                tvecs[i, 0, :],
                self.marker_size,
                self.frame_type,
            )
        return frame

    def drawMarkerAxes(
        self,
        img,
        corners,
        rvec,
        tvec,
        axis_length=0.15,
        frame_type="NED",
    ) -> np.ndarray:
        average_corner = np.mean(corners, axis=1)
        axis = None
        if frame_type == "NED":
            axis = np.float32(
                [[0, axis_length, 0], [axis_length, 0, 0], [0, 0, -axis_length]]
            ).reshape(-1, 3)
        elif frame_type == "ENU":
            axis = np.float32(
                [[axis_length, 0, 0], [0, axis_length, 0], [0, 0, axis_length]]
            ).reshape(-1, 3)

        # project 3D points to image plane
        imgpts, _ = cv2.projectPoints(
            axis, rvec, tvec, self.camera_matrix, self.camera_distortion
        )

        corner = tuple(average_corner.ravel().astype(int))
        img = cv2.line(
            img, corner, tuple(imgpts[0].ravel().astype(int)), (0, 0, 255), 5
        )
        img = cv2.line(
            img, corner, tuple(imgpts[1].ravel().astype(int)), (0, 255, 0), 5
        )
        img = cv2.line(
            img, corner, tuple(imgpts[2].ravel().astype(int)), (255, 0, 0), 5
        )
        return img
