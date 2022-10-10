"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-10 08:18:56
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
        self.service2super = dict()
        self.super2service = dict()

    @value_dispatch
    def handle_msg(self, type, msg, addr):
        logging.error(f"unexpected msg type:{type} with msg:{msg}, please check.")
        return False

    @handle_msg.register(Msg.INIT_SESSION_REQUEST)
    def _(self, type, msg, addr):
        # 转发包体
        if addr in self.service2super.keys():
            super = self.service2super[addr]
        else:
            super = self.super
            self.service2super[addr] = super
            self.super2service[super] = addr
        self.rpc.send(msg, super)
        logging.info(
            f"cross node {self.addr} handle msg {type} forward package to super {super}"
        )

    @handle_msg.register(Msg.INIT_SEESION_RESPONSE)
    def _(self, type, msg, addr):
        # 转发包体
        self.rpc.send(msg, self.service)


if __name__ == "__main__":
    cross = Cross()
    breakpoint()
