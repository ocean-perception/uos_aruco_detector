from pathlib import Path
import json
import numpy as np


class Configuration:
    def __init__(self, filename):
        if not Path(filename).exists():
            raise FileNotFoundError(f"Configuration file {filename} not found")

        self.filename = filename
        self.load()

    def load(self):
        config = json.load(self.filename)
        # -- Define path where all code is stored
        path = config["Main Code Path"]
        storage = config["USB Storage Path"]
        # --- Define Tags
        marker_size = float(config["Marker Size"])  # [m]
        CAL = float(config["CAL"])
        SHUTDOWN = float(config["SHUTDOWN"])
        OK = float(config["OK"])
        ENU = float(config["ENU"])
        NED = float(config["NED"])
        SEND = float(config["SEND"])
        # -- Logging variable, 1 -> logging is on; 0--> logging is off
        logging = float(config["Enable Logging"])
        # -- Broadcast position every # seconds. Default is 1, change via Aruco Code
        F_delay = float(config["Default Broadcasting Period"])
        coord_system = "ENU"
        # -- List of tags that modify frequency and their corresponding value [TAG_ID, SECONDS]
        frequencies = np.array([[30, 0], [31, 1], [32, 2], [33, 5], [34, 10], [35, -1]])
