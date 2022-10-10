"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-10 09:21:12
Description: 业务链节点
"""
from nodes.base import Base
from utils import value_dispatch, Msg
from framework import factory
from common import config, logging


@factory("nodes.Service")
class Service(Base):
    def __init__(self, addr=None, config=config) -> None:
        super().__init__(addr, config)
        self.client2cross=dict()
        self.cross2client=dict()

    @value_dispatch
    def handle_msg(self, type, msg, addr):
        logging.error(f"unexpected msg type:{type} with msg:{msg}, please check.")
        return False

    @handle_msg.register(Msg.INIT_SESSION_REQUEST)
    def _(self, type, msg, addr):
        # 转发包体
        if addr in self.client2cross.keys():
            cross = self.client2cross[addr]
        else:
            cross = self.cross
            self.client2cross[addr] = cross
            self.cross2client[cross] = addr
        self.rpc.send(msg, cross)
        logging.info(f"service node {self.addr} handle msg {type} forward package to cross {cross}")

    @handle_msg.register(Msg.INIT_SEESION_RESPONSE)
    def _(self, type, msg, addr):
        client_addr = msg.get("client-addr", None)
        if client_addr is None:
            logging.error(f"{type} have not client-addr section. Handle msg failed.")
        self.rpc.send(msg, tuple(client_addr))
