"""
Author: lpdink
Date: 2022-10-07 02:34:16
LastEditors: lpdink
LastEditTime: 2022-10-10 08:36:18
Description: 后端业务主服务器，用于批量创建及管理节点，监测节点性能。
"""
from common import logging
from framework import factory
from multiprocessing import Process
import random


class Server:
    _instance = None

    def __new__(cls, config, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self, config) -> None:
        factory.create_obj_from_config(config)
        self._service_group = factory["service_group"]
        self._super_group = factory["super_group"]
        self._cross_group = factory["cross_group"]
        self._all_node_group = (
            self._service_group + self._super_group + self._cross_group
        )
        self._process_pool = []
        # 将网络情况告知所有节点
        self.set_network_graph()

    def set_network_graph(self):
        service_addrs = [node.addr for node in self._service_group]
        super_addrs = [node.addr for node in self._super_group]
        cross_addrs = [node.addr for node in self._cross_group]
        network = {
            "service_addrs": service_addrs,
            "super_addrs": super_addrs,
            "cross_addrs": cross_addrs,
        }
        for node in self._all_node_group:
            node.set_network_graph(network)

    @property
    def service(self):
        return random.choice(self._service_group)

    @property
    def super(self):
        return random.choice(self._super_group)

    @property
    def cross(self):
        return random.choice(self._cross_group)

    def run(self, behind=False):
        for node in self._all_node_group:
            node_process = Process(target=node.run, daemon=behind)
            self._process_pool.append(node_process)
        for process in self._process_pool:
            process.start()
        logging.info("Server begin running.")

    def shut_down(self):
        for process in self._process_pool:
            process.terminate()
        logging.info("Server shutdown.")
