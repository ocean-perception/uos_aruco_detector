import json
import socket
import time


def main():
    # Parameters
    params = {
        "port": 50000,
        "timeout": 0.1,
    }

    # -- UDP
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # -- Enable port reusage
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # -- Enable broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.settimeout(params["timeout"])
    client.bind(("", params["port"]))

    while True:
        broadcast_data, _ = client.recvfrom(1024)
        result = json.loads(broadcast_data)
        print("Received: %s" % result)
        time.sleep(0.1)


if __name__ == "__main__":
    main()
