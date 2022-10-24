"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-24 03:54:15
Description: 跨链节点
"""
from common import config, logging
from framework import factory
from nodes.base import Base
from utils import Msg, value_dispatch


@factory("nodes.Cross")
class Cross(Base):
    def __init__(self, addr=None, config=config) -> None:
        super().__init__(addr, config)

    @value_dispatch
    def handle_msg(self, type, msg, addr):
        logging.error(f"unexpected msg type:{type} with msg:{msg}, please check.")
        return False

    @handle_msg.register(Msg.INIT_SESSION_REQUEST)
    def _(self, type, msg, addr):
        # 转发包体
        center = self.center
        self.rpc.send(msg, center)
        logging.info(
            f"cross node {self.addr} handle msg {type} forward package to center {center}"
        )

    @handle_msg.register(Msg.SERVICE_FORWARD_TO_SUPER)
    def _(self, type, msg, addr):
        self.rpc.send(msg, self.super)

    @handle_msg.register(Msg.SUPER_DELETE_TO_SERVICE)
    @handle_msg.register(Msg.INIT_SEESION_RESPONSE)
    def _(self, type, msg, addr):
        # 转发包体
        self.rpc.send(msg, self.service)


if __name__ == "__main__":
    cross = Cross()
    breakpoint()
