import socket
import json


class UDPBroadcastServer:
    def __init__(self, ip, port):
        # -- Enable port reusage
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        # -- Enable broadcasting mode
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.socket.connect(("8.8.8.8", 80))
        ip = self.socket.getsockname()[0]
        self.socket.settimeout(None)
        self.ip = ip
        self.port = port
        broadcast_data = {}

    def broadcast(self, message):
        # -- Broadcast the dictionary as a bytes-like object (string-like info) and empties
        broadcast_string = json.dumps(message, indent=3)

        self.socket.sendto(
            broadcast_string.encode("utf-8"),
            (self.ip, self.port),
        )
