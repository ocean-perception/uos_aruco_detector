import csv

import cv2
import numpy as np

from .rotations import rotationMatrixToEulerAngles


class OriginReference:
    def __init__(self, path):
        self.path = path
        self.angles = np.array([0, 0, 0])
        self.tvec = np.array([0, 0, 0])
        self.rvec = np.array([0, 0, 0])
        self.initialised = False
        self.frame = "ENU"

    def set(self, rvec, tvec):
        # -- Store the origin location
        with open(
            self.path / "origin.csv", "w", encoding="utf-8", newline=""
        ) as stored_origin:
            # -- Flip the y and z axis to ensure standard orientation of axis
            tvec_flipped = tvec * np.array([1, -1, -1])
            writer = csv.writer(stored_origin)
            writer.writerow(rvec)
            writer.writerow(tvec_flipped)
            writer.writerow(tvec)

            # -- Obtain the rotation matrix tag->camera
            R_ct_ini = np.matrix(cv2.Rodrigues(rvec)[0])
            R_tc_ini = R_ct_ini.T

            # -- Get the attitude in terms of euler 321 (Needs to be flipped first)
            R_flip = np.zeros((3, 3), dtype=np.float32)
            R_flip[0, 0] = 1.0
            R_flip[1, 1] = -1.0
            R_flip[2, 2] = -1.0
            (
                roll,
                pitch,
                yaw,
            ) = rotationMatrixToEulerAngles(R_flip * R_tc_ini)
            self.angles = np.array([roll, pitch, yaw])
            self.tvec = tvec
            self.rvec = rvec
            self.initialised = True

    def get_relative_position(self, rvec, tvec_flipped):
        # -- Unpack the output, get only the first
        tvec = tvec_flipped * np.array([1, -1, -1])

        # -- Obtain the rotation matrix tag->camera
        R_ct = np.matrix(cv2.Rodrigues(rvec)[0])
        R_tc = R_ct.T

        # --- 180 deg rotation matrix around the x axis
        R_flip = np.zeros((3, 3), dtype=np.float32)
        R_flip[0, 0] = 1.0
        R_flip[1, 1] = -1.0
        R_flip[2, 2] = -1.0

        # -- Get the attitude in terms of euler 321 (Needs to be flipped first)
        roll_marker, pitch_marker, yaw_marker = rotationMatrixToEulerAngles(
            R_flip * R_tc
        )
        angles = np.array([roll_marker, pitch_marker, yaw_marker])

        # -- Calculates position and attitude wrt to origin
        if self.frame == "ENU":
            tag_position = tvec - self.tvec
            tag_rotation = angles - self.angles
        else:
            tag_position = tvec_flipped - self.tvec * np.array([1, -1, -1])
            tag_rotation = angles - self.angles

        return tag_position, tag_rotation

    def get():
        return
