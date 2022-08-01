# Aruco detector
ArUco marker detection and localisation.

Given a calibration setup this program will detect ArUco markers, log and broadcast its positions.
By default, the program will shutdown the computer it is running in. If you want to disable this behaviour, please supply the flag `--no-shutdown` when running it.


## How to install
To install this software, run the following in a terminal:

```bash
pip install git+https://github.com/miquelmassot/uos_aruco_detector.git
```

## Usage
To run the program, connect a webcam to your computer and type `uos_aruco_detector` in a terminal.

If you don't want the program to shutdown your computer at the end, type `uos_aruco_detector --no-shutdown` instead.

```
uos_aruco_detector [-h] [--no-shutdown]

options:
  -h, --help     show this help message and exit
  --no-shutdown  Don't shutdown at the end of the program
```

## Reference frames
```
Here are the defined reference frames:

TAG:
                A y
                |
                |
                |tag center
                O---------> x

CAMERA:


                X--------> x
                | frame center
                |
                |
                V y
```