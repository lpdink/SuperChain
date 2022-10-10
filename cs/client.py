"""
Author: lpdink
Date: 2022-10-07 02:16:01
LastEditors: lpdink
LastEditTime: 2022-10-10 09:29:00
Description: 业务链客户端。模拟。
"""
from common import logging
from framework import Rpc, Session


class Client:
    def __init__(self, addr=None) -> None:
        self.addr = addr

    @property
    def key(self):
        return self.session.key

    def init_session(self, server_addr):
        self.session = Session(self.addr, server_addr)
        logging.info("session created, begin init")
        # 创建一个session，负责控制init阶段
        self.session.init()
        return self.session

    def stop_session(self):
        self.session.c_rpc.close()

    def exit(self):
        del self
