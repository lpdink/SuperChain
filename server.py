from common import get_config, logging
from common.KeyManager import KeyManager
from cs import Client, Server
from nodes import *
from utils import sha256


def run_server():
    try:
        obj_config = get_config("./resources/node.json")
        server = Server(obj_config)
        server.show_service_addr()
        server.run(behind=False)
    except KeyboardInterrupt:
        server.shut_down()


if __name__ == "__main__":
    run_server()
