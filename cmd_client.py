import os
import json
import socket
import time
from multiprocessing import Process

from common import config, logging
from utils import ConsensusMsg, UserMessage

BATCH_SIZE = config.consensus.batch_size
PACKAGE_SIZE = config.consensus.package_size

def to_yellow(text):
    return f"\033[33m{text}\033[0m"

def to_red(text):
    return f"\033[31m{text}\033[0m"

def to_green(text):
    return f"\033[32m{text}\033[0m"

def main():
    sk_get = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk_get.bind(("127.0.0.1", 0))
    sk_get.setblocking(False)
    while True:
        try:
            port = int(input(to_yellow("请输入审查链POSTBOX端口，如果您不知道，请先执行python consensus_server.py：\n> ")).strip())
            break
        except ValueError:
            print(to_red("您输入的端口必须是一个整数"))

    dst_addr = ('127.0.0.1', port)
    while True:
        cmd = input(to_yellow("请输入您准备提交审查的数据，任意信息皆可。\n如果您想退出程序，请输入q：\n> "))
        if cmd.strip().lower()=='q':
            print(to_yellow("命令行客户端已退出"))
            exit()

        
        data = {
            "type": ConsensusMsg.USER_REQUEST,
            "data": [cmd],
            "client": sk_get.getsockname(),
            "true_addr": sk_get.getsockname()
        }
        data = json.dumps(data).encode("utf-8")
        # for _ in range(BATCH_SIZE*PACKAGE_SIZE):
        while True:
            sk_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sk_send.connect(tuple(dst_addr))
            sk_send.sendall(data)
            sk_send.shutdown(socket.SHUT_RDWR)
            sk_send.close()
            try:
                data, addr = sk_get.recvfrom(65535)
            except BlockingIOError:
                pass
            else:
                print(to_green(f"从服务器 {addr} 收到了共识信息：{data}"))
                print(to_yellow(f"由于审查链对高并发场景特殊优化，对单条请求的响应速度不能代表性能情况."))
                os.system("killall -9 python")
                break
            time.sleep(0.0001)
    # pass

if __name__=="__main__":
    main()
