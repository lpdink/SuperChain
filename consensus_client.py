import json
import socket
import time
from multiprocessing import Process

from common import logging
from utils import ConsensusMsg, UserMessage

DST_ADDR = ("127.0.0.1", 37070)
BATCH_SIZE = 512
TEST_TIME = 30

sk_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sk_send.bind(("127.0.0.1", 0))
sk_get = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sk_get.bind(("127.0.0.1", 0))


def send():
    while True:
        data = {
            "type": ConsensusMsg.USER_REQUEST,
            "data": UserMessage.random_msg(),
            "client": sk_get.getsockname(),
        }
        data = json.dumps(data).encode("utf-8")
        sk_send.sendto(data, tuple(DST_ADDR))
        time.sleep(0.0001)


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
                logging.warning(f"tps:{package_num*BATCH_SIZE/time_used}")
                exit()


if __name__ == "__main__":
    send_process = Process(target=send)
    get_process = Process(target=get)
    send_process.start()
    get_process.start()
