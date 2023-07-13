import csv

import cv2
import numpy as np
from scipy.spatial.transform import Rotation

from .rotations import rotationMatrixToEulerAngles


def inverse_prespective(rvec, tvec):
    R, _ = cv2.Rodrigues(rvec)
    R = np.matrix(R).T
    invTvec = np.dot(-R, np.matrix(tvec))
    invRvec, _ = cv2.Rodrigues(R)
    return invRvec, invTvec


def relative_position(rvec1, tvec1, rvec2, tvec2):
    """Calculates the relative position of the second marker wrt the first one.

    Args:
        rvec1 (np.ndarray): Rotation vector of the first marker.
        tvec1 (np.ndarray): Translation vector of the first marker.
        rvec2 (np.ndarray): Rotation vector of the second marker.
        tvec2 (np.ndarray): Translation vector of the second marker.

    Returns:
        np.ndarray: Rotation vector of the second marker wrt the first one.
        np.ndarray: Translation vector of the second marker wrt the first one.
    """
    rvec1, tvec1 = rvec1.reshape((3, 1)), tvec1.reshape((3, 1))
    rvec2, tvec2 = rvec2.reshape((3, 1)), tvec2.reshape((3, 1))
    # Inverse the second marker, the right one in the image
    invRvec, invTvec = inverse_prespective(rvec2, tvec2)
    info = cv2.composeRT(rvec1, tvec1, invRvec, invTvec)
    composed_rvec, composed_tvec = info[0], info[1]
    composed_rvec = composed_rvec.reshape((3, 1))
    composed_tvec = composed_tvec.reshape((3, 1))
    return composed_rvec, composed_tvec


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
            self.tvec = tvec
            self.rvec = rvec
            self.initialised = True

    def get_relative_position(self, rvec, tvec):
        if not self.initialised:
            return None, None

        # -- Get the relative position of the second marker wrt the first one
        composed_rvec, composed_tvec = relative_position(
            rvec,
            tvec,
            self.rvec,
            self.tvec,
        )

        rot = cv2.Rodrigues(composed_rvec)[0]
        tag_position = composed_tvec

        if self.frame == "NED":
            # Rotation matrix for ENU to NED
            R = np.array(
                [
                    [0, 1, 0],
                    [1, 0, 0],
                    [0, 0, -1],
                ]
            )
            # Transform the position and rotation to NED
            tag_position = R @ composed_tvec
            rot = R @ rot

        r = Rotation.from_matrix(rot)
        angles = r.as_euler("XYZ", degrees=True)
        tag_rotation = np.array([angles[0], angles[1], angles[2]])
        tag_position = tag_position.reshape((3,))

        print(self.frame, tag_position, tag_rotation)

        return tag_position, tag_rotation

    def get():
        return
