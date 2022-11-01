from common import get_config, logging
from cs import Server


def run_server():
    try:
        obj_config = get_config("./resources/node.json")
        server = Server(obj_config)
        server.run(behind=False)
        server.show_service_addr()
    except KeyboardInterrupt:
        server.shut_down()


if __name__ == "__main__":
    run_server()
