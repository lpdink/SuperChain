import json
import socket
import time
from multiprocessing import Process

from common import config, logging
from utils import ConsensusMsg, UserMessage

BATCH_SIZE = config.consensus.batch_size
PACKAGE_SIZE = config.consensus.package_size
TEST_TIME = 10

sk_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sk_send.bind(("127.0.0.1", 0))
sk_get = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sk_get.bind(("127.0.0.1", 0))

def to_yellow(text):
    return f"\033[33m{text}\033[0m"

def to_red(text):
    return f"\033[31m{text}\033[0m"

while True:
    try:
        port = int(input(to_yellow("请输入审查链POSTBOX端口，如果您不知道，请先执行python consensus_server.py：\n> ")).strip())
        DST_ADDR = ("127.0.0.1", port)
        break
    except ValueError:
        print(to_red("您输入的端口必须是一个整数"))


def send():
    while True:
        data = {
            "type": ConsensusMsg.USER_REQUEST,
            "data": UserMessage.random_msg(),
            "client": sk_get.getsockname(),
        }
        data = json.dumps(data).encode("utf-8")
        sk_send.sendto(data, tuple(DST_ADDR))
        time.sleep(0.000001)


def get():
    package_num = 0
    first_package_time = None
    last_time, this_time = None, None
    while True:
        data, addr = sk_get.recvfrom(65535)
        package_num += 1
        # 单包时间
        if last_time is None:
            last_time = time.perf_counter()
        else:
            this_time = time.perf_counter()
            logging.warning(f"time use:{this_time-last_time}")
            last_time = time.perf_counter()
        # 总时间
        if first_package_time is None:
            first_package_time = time.perf_counter()
        else:
            last_package_time = time.perf_counter()
            time_used = last_package_time - first_package_time
            if time_used > TEST_TIME:
                logging.warning(
                    f"package_num :{package_num}, time used: {time_used} s."
                )
                logging.warning(f"tps:{package_num*BATCH_SIZE*PACKAGE_SIZE/time_used}")
                exit()

if __name__ == "__main__":
    send_process = Process(target=send)
    get_process = Process(target=get)
    send_process.start()
    get_process.start()
