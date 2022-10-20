"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-20 08:20:00
Description: 跨链节点
"""
from nodes.base import Base
from framework import factory
from common import config, logging
from utils import value_dispatch, Msg


@factory("nodes.Cross")
class Cross(Base):
    def __init__(self, addr=None, config=config) -> None:
        super().__init__(addr, config)

    @value_dispatch
    def handle_msg(self, type, msg, addr):
        logging.error(f"unexpected msg type:{type} with msg:{msg}, please check.")
        return False

    @handle_msg.register(Msg.SERVICE_FORWARD_TO_SUPER)
    @handle_msg.register(Msg.INIT_SESSION_REQUEST)
    def _(self, type, msg, addr):
        # 转发包体
        super = self.super
        self.rpc.send(msg, super)
        logging.warning(
            f"cross node {self.addr} handle msg {type} forward package to super {super}"
        )

    @handle_msg.register(Msg.INIT_SEESION_RESPONSE)
    def _(self, type, msg, addr):
        # 转发包体
        self.rpc.send(msg, self.service)


if __name__ == "__main__":
    cross = Cross()
    breakpoint()
