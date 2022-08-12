import numpy as np
import cv2
import glob
import sys
import argparse


def yaml(size, intrinsics, distortion, num_images, avg_reprojection_error):
    calmessage = (
        "%YAML:1.0\n"
        + "image_width: "
        + str(size[0])
        + "\n"
        + "image_height: "
        + str(size[1])
        + "\n"
        + "camera_matrix: !!opencv-matrix\n"
        + "  rows: 3\n"
        + "  cols: 3\n"
        + "  dt: d\n"
        + "  data: ["
        + ", ".join(["%8f" % i for i in intrinsics.reshape(1, 9)[0]])
        + "]\n"
        + "distortion_model: "
        + ("rational_polynomial" if distortion.size > 5 else "plumb_bob")
        + "\n"
        + "distortion_coefficients: !!opencv-matrix\n"
        + "  rows: 1\n"
        + "  cols: 5\n"
        + "  dt: d\n"
        + "  data: ["
        + ", ".join(["%8f" % distortion[i, 0] for i in range(distortion.shape[0])])
        + "]\n"
        + 'date: "'
        + Console.get_date()
        + '" \n'
        + "number_of_images: "
        + str(num_images)
        + "\n"
        + "avg_reprojection_error: "
        + str(avg_reprojection_error)
        + "\n"
        + ""
    )
    return calmessage


def main():
    parser = argparse.ArgumentParser(description="Calibrate camera using aruco markers")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="Folder where the images are stored",
    )
    parser.add_argument(
        "-e", "--extension", type=str, default="jpg", help="image extension"
    )
    parser.add_argument(
        "--nx", type=int, default=9, help="Number of inside corners in x"
    )
    parser.add_argument(
        "--ny", type=int, default=6, help="Number of inside corners in y"
    )
    parser.add_argument(
        "--size", type=float, default=0.03, help="Size of chessboard squares"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="camera_calibration.yaml",
        help="path to output file",
    )
    args = parser.parse_args()

    # If no arguments are provided, print help
    if len(sys.argv) == 1:
        parser.print_help()
        print(
            "The script will look for every image in the provided folder and will",
            "show the pattern found.\n",
            "Users can skip the image pressing ESC or accepting the image with RETURN.",
            "At the end the end the following files are created:\n",
            "  - camera_calibration.yaml:\n",
            "      Contains the calibration matrix and distortion coefficients\n",
        )
        sys.exit(1)

    if args.input is None:
        print("Please specify an input folder")
        sys.exit(1)
    if args.nx is None:
        print("Please specify nx")
        sys.exit(1)
    if args.ny is None:
        print("Please specify ny")
        sys.exit(1)
    if args.size is None:
        print("Please specify size")
        sys.exit(1)
    if args.extension is None:
        print("Please specify extension")
        sys.exit(1)

    n_rows = args.nx
    n_cols = args.ny
    dimension = args.size
    image_folder = args.input
    image_extension = args.extension
    images = glob.glob(str(image_folder / "*." + image_extension))

    print(len(images))
    if len(images) < 9:
        print("Not enough images were found: at least 9 shall be provided!!!")
        sys.exit()

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, dimension, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((n_rows * n_cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:n_cols, 0:n_rows].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    nPatternFound = 0
    imgNotGood = images[1]

    for fname in images:
        if "calibresult" in fname:
            continue
        # -- Read the file and convert in greyscale
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        print("Reading image ", fname)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (n_cols, n_rows), None)

        # If found, add object points, image points (after refining them)
        if ret == True:
            print("Pattern found! Press ESC to skip or ENTER to accept")
            # --- Sometimes, Harris cornes fails with crappy pictures, so
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

            # Draw and display the corners
            cv2.drawChessboardCorners(img, (n_cols, n_rows), corners2, ret)
            cv2.imshow("img", img)
            k = cv2.waitKey(0) & 0xFF
            if k == 27:  # -- ESC Button
                print("Image Skipped")
                imgNotGood = fname

            print("Image accepted")
            nPatternFound += 1
            objpoints.append(objp)
            imgpoints.append(corners2)
        else:
            imgNotGood = fname

    cv2.destroyAllWindows()

    if nPatternFound > 1:
        print("Found %d good images" % (nPatternFound))
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None
        )

        # Undistort an image
        img = cv2.imread(imgNotGood)
        h, w = img.shape[:2]
        print("Image to undistort: ", imgNotGood)
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

        # undistort
        mapx, mapy = cv2.initUndistortRectifyMap(
            mtx, dist, None, newcameramtx, (w, h), 5
        )
        dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

        # crop the image
        x, y, w, h = roi
        dst = dst[y : y + h, x : x + w]
        print("ROI: ", x, y, w, h)

        cv2.imwrite(image_folder + "/calibresult.png", dst)
        print("Calibrated picture saved as calibresult.jpg")
        print("Calibration Matrix: ")
        print(mtx)
        print("Disortion: ", dist)

        # --------- Save result
        filename = image_folder + "/cameraMatrix.txt"
        np.savetxt(filename, mtx, delimiter=",")
        filename = image_folder + "/cameraDistortion.txt"
        np.savetxt(filename, dist, delimiter=",")

        mean_error = 0
        for i in range(len(objpoints)):
            imgpoints2, _ = cv2.projectPoints(
                objpoints[i], rvecs[i], tvecs[i], mtx, dist
            )
            error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            mean_error += error

        print("total error: ", mean_error / len(objpoints))

    else:
        print("In order to calibrate you need at least 9 good pictures... try again")


if __name__ == "__main__":
    main()
