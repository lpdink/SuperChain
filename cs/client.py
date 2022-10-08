"""
Author: lpdink
Date: 2022-10-07 02:16:01
LastEditors: lpdink
LastEditTime: 2022-10-08 08:48:45
Description: 业务链客户端。模拟。
"""
from framework import Rpc, Session


class Client:
    def __init__(self, addr=None) -> None:
        self.addr = addr

    def _recv(self):
        return None

    def init_session(self, server_addr):
        self.session = Session(self.addr, server_addr)
        # 创建一个session，负责控制init阶段
        return self.session

    def stop_session(self):
        pass

    def exit(self):
        pass
