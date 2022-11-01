"""
Author: lpdink
Date: 2022-10-28 08:21:46
LastEditors: lpdink
LastEditTime: 2022-11-01 07:35:28
Description: 
"""
import asyncio
import json
import os
import random

from common import config, logging
from utils import value_dispatch

from .node import nodefactory


@nodefactory("protocols.Base")
class BaseProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport
        if not hasattr(self, "_network"):
            addr_file_path = os.path.join(
                os.path.dirname(__file__), "../resources/.addr.json"
            )
            with open(addr_file_path, "r") as file:
                self._netwrok = json.load(file)
            self._service_addrs = list(
                map(lambda x: tuple(x), self._netwrok["ServiceProtocol"])
            )
            self._super_addrs = list(
                map(lambda x: tuple(x), self._netwrok["SuperProtocol"])
            )
            self._cross_addrs = list(
                map(lambda x: tuple(x), self._netwrok["CrossProtocol"])
            )

    def datagram_received(self, data, addr):
        data = json.loads(data.decode())
        msg_type = data["type"]
        self.handle_msg(msg_type, data, addr)

    def handle_msg(self, type, msg, addr):
        raise NotImplementedError("handle_msg should rewrite in sub-class")

    def sendto(self, msg, addr):
        msg = json.dumps(msg).encode("utf-8")
        self.transport.sendto(msg, tuple(addr))
        logging.info(f"{self.addr} node send {msg} to {tuple(addr)}")

    @property
    def addr(self):
        return self.transport.get_extra_info("sockname")

    @property
    def port(self):
        return self.transport.get_extra_info("sockname")[1]

    @property
    def service(self):
        return tuple(random.choice(self._service_addrs))

    @property
    def super(self):
        return tuple(random.choice(self._super_addrs))

    @property
    def cross(self):
        return tuple(random.choice(self._cross_addrs))

    @property
    def center(self):
        # center 只有一个
        return tuple(self._netwrok["CenterProtocol"][0])
