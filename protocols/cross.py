"""
Author: lpdink
Date: 2022-10-28 08:21:54
LastEditors: lpdink
LastEditTime: 2022-10-28 09:29:56
Description: 
"""
from common import KeyManager, config, logging
from utils import Msg, value_dispatch

from .base import BaseProtocol
from .node import nodefactory


@nodefactory("protocols.Cross")
class CrossProtocol(BaseProtocol):
    @value_dispatch
    def handle_msg(self, type, msg, addr):
        logging.error(f"unexpected msg type:{type} with msg:{msg}, please check.")
        return False

    @handle_msg.register(Msg.INIT_SESSION_REQUEST)
    def _(self, type, msg, addr):
        # 转发包体
        center = self.center
        self.sendto(msg, center)
        logging.info(
            f"cross node {self.addr} handle msg {type} forward package to center {center}"
        )

    @handle_msg.register(Msg.SERVICE_FORWARD_TO_SUPER)
    def _(self, type, msg, addr):
        self.sendto(msg, self.super)

    @handle_msg.register(Msg.SUPER_DELETE_TO_SERVICE)
    @handle_msg.register(Msg.INIT_SEESION_RESPONSE)
    def _(self, type, msg, addr):
        # 转发包体
        self.sendto(msg, self.service)
