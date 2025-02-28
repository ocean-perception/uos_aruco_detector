# Aruco detector
ArUco marker detection and localisation.

Given a calibration setup this program will detect ArUco markers, log and broadcast its positions.
By default, the program will shutdown the computer it is running in. If you want to disable this behaviour, please supply the flag `--no-shutdown` when running it.

## 1. Setup your Raspberry Pi

Install the rpi operating system by downloading the installer here:
https://www.raspberrypi.com/software/

Install 'Raspberry Pi OS (Legacy, 32bit) Debian Bullseye port'

To access wifi, once logged on select your network (e.g., oplab-net), and from the rpi logo (top left) select Preferences -> Raspberry Pi Configuration -> Interfaces and enable VNC (click OK)

Add where the software will go to the path by typing in a terminal

```bash
nano .bashrc
```
and at the bottom adding this line

```bash
export PATH="/home/pi/.local/bin:$PATH"
```

Install chrony for time synchronisation

```bash
sudo apt-get update
sudo apt-get install chrony
sudo systemctl start chrony
sudo systemctl enable chrony
```

Install some base libraries
```bash
sudo apt-get update
sudo apt-get install libblas-dev==3.9.0-3+deb11u1 liblapack-dev==3.9.0-3+deb11u1 libatlas-base-dev==3.10.3-10+rpi1 libhdf5-dev==1.10.6+repack-4+deb11u1
```
Setup crontab to autorun the software on boot
```bash
crontab -e
```
add this at bottom

```bash
@reboot DISPLAY=:0 /bin/bash /home/pi/autostart_aruco.sh > /home/pi/cron_usr.log 2>&1
```
and add the file autostart_aruco.sh from this repository to the /home/pi directory

Make it executable with 
```bash
chmod +x autostart_aruco.sh
```

run the autostart_aruco.sh from the terminal, 
```bash
./autostart_aruco.sh
```


It should install the software by itself and you can start using it.

## How to install
To install this software manually, run the following in a terminal:

```bash
pip install git+https://github.com/ocean-perception/uos_aruco_detector.git
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

## Aruco IDs
Check the configuration in the [configuration.yaml](https://github.com/ocean-perception/uos_aruco_detector/blob/main/src/uos_aruco_detector/configuration/configuration.yaml) file 


| Tag                  | ID | Function                             |
|:---------------------|:--:|:-------------------------------------|
| OK                   | 12 | Setting confirmation                 |
| SHUTDOWN             | 13 | Shutdown RPi                         |
| FRAME_ENU            | 14 | Publish in ENU                       |
| FRAME_NED            | 15 | Publish in NED                       |
| CALIBRATION          | 17 | Calibrate origin frame               |
| BROADCAST_NEVER      | 22 | Do not broadcast unless OK is shown  |
| BROADCAST_FREQ_01_HZ | 18 | Limit broadcast at 0.1 Hz            |
| BROADCAST_FREQ_02_HZ | 19 | Limit broadcast at 0.2 Hz            |
| BROADCAST_FREQ_1_HZ  | 20 | Limit broadcast at 1 Hz              |
| BROADCAST_FREQ_5_HZ  | 21 | Limit broadcast at 5 Hz              |
| BROADCAST_ALWAYS     | 16 | Broadcast continuously               |

## Check reception
In a bash terminal, you can check the UDP broadcast using netcat. Type the following:
```bash
nc -ul 50000
```
where `50000` is the default port. Change this number if the port changes in your setup.


### Message contents
The fields are
```
  "epoch [s]",
  "elapsed [s]",
  "x [m]",
  "y [m]",
  "z [m]",
  "roll [deg]",
  "pitch [deg]",
  "yaw [deg]",
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
