import json
import socket
import time

from common import logging
from utils import ConsensusMsg, UserMessage

DST_ADDR = ("127.0.0.1", 63432)
BATCH_SIZE = 512
TEST_TIME = 30

if __name__ == "__main__":
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk.bind(("127.0.0.1", 0))
    count = 0
    total_package_num = 0
    first_package_time = None
    while True:
        data = {"type": ConsensusMsg.USER_REQUEST, "data": UserMessage.random_msg()}
        data = json.dumps(data).encode("utf-8")
        start = time.perf_counter()
        sk.sendto(data, tuple(DST_ADDR))
        count += 1
        if count > BATCH_SIZE:
            data, addr = sk.recvfrom(65535)
            if addr is not None:
                total_package_num += 1
                if first_package_time is None:
                    first_package_time = time.perf_counter()
                else:
                    last_package_time = time.perf_counter()
                    time_used = last_package_time - first_package_time
                    if time_used > TEST_TIME:
                        logging.warning(
                            f"package_num :{total_package_num}, time used: {time_used} s."
                        )
                        logging.warning(f"tps:{total_package_num*BATCH_SIZE/time_used}")
                        exit()
                end = time.perf_counter()
                logging.warning(f"time use:{end-start}")
                start = time.perf_counter()
                count = 0
        # time.sleep(0.0001)
