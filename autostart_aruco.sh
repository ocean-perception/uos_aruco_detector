#!/bin/bash

wget -q --spider http://www.google.com

if [ $? -eq 0 ]; then
	echo "Online"
	pip install -U git+https://github.com/ocean-perception/uos_aruco_detector.git
else
	echo "Offline"
fi
sleep 30
uos_aruco_detector
