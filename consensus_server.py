from common import get_config, logging
from cs import ConsensusServer


def run_server():
    try:
        obj_config = get_config("./resources/consensus_node.json")
        server = ConsensusServer(obj_config)
        server.run(behind=False)
        server.show_postbox_addr()
    except KeyboardInterrupt:
        server.shut_down()


if __name__ == "__main__":
    run_server()
