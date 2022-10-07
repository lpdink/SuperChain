"""
Author: lpdink
Date: 2022-10-07 02:16:01
LastEditors: lpdink
LastEditTime: 2022-10-07 02:16:19
Description: 业务链客户端。模拟。
"""
from framework import Rpc


class Client:
    def __init__(self, addr=None) -> None:
        # 为None时，随机分配空闲端口
        self.rpc = Rpc(addr)
        self.key = None

    def bind(self, service_addr):
        self.service_addr = service_addr

    def _recv(self):
        return None

    def init_session(self):
        return None

    def stop_session(self):
        pass

    def exit(self):
        pass
