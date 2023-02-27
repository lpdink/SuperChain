import socket
import json
import time


if __name__=="__main__":
    data = {"data":1}
    data = json.dumps(data).encode("utf-8")
    addr = ("127.0.0.1", 9999)
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk.bind(("127.0.0.1", 0))
    while True:
        sk.sendto(data, tuple(addr))
