"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-13 06:49:44
Description: 基类节点
"""
import random

from common import config, logging
from framework import Rpc, factory
from utils import value_dispatch


@factory("nodes.Base")
class Base:
    def __init__(self, addr=None, config=config) -> None:
        self.rpc = Rpc(addr, config.connection)

    def set_network_graph(self, network_graph):
        self.network_graph = network_graph
        self._service_addrs = self.network_graph.get("service_addrs", None)
        self._super_addrs = self.network_graph.get("super_addrs", None)
        self._cross_addrs = self.network_graph.get("cross_addrs", None)
        self.center = self.network_graph.get("center_addrs", None)[0]

    def handle_msg(self, type, msg, addr):
        raise NotImplementedError("handle_msg should rewrite in sub-class")

    @property
    def port(self):
        return self.rpc.port

    @property
    def addr(self):
        return self.rpc.addr

    @property
    def service(self):
        return random.choice(self._service_addrs)

    @property
    def super(self):
        return random.choice(self._super_addrs)

    @property
    def cross(self):
        return random.choice(self._cross_addrs)

    # 持续接收，并根据策略处理
    def run(self):
        while True:
            try:
                try:
                    data, addr = self.rpc.recv()
                except:
                    data, addr = {}, None
                if addr is not None:
                    if isinstance(data, dict):
                        msg_type = data["type"]
                        msg = data
                        self.handle_msg(msg_type, msg, addr)
                    # logging.info(f"{self.rpc.addr} receive {data} from addr {addr}")
            except KeyboardInterrupt:
                self.rpc.close()


if __name__ == "__main__":
    base = Base()
    base.run()
