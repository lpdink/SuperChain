"""
Author: lpdink
Date: 2022-10-07 02:34:16
LastEditors: lpdink
LastEditTime: 2022-10-28 10:41:27
Description: 后端业务主服务器，用于批量创建及管理节点，监测节点性能。
"""
import json
import os
import random
import socket
import time
from multiprocessing import Process

from common import logging
from protocols import nodefactory


class Server:
    _instance = None

    def __new__(cls, config, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self, config) -> None:
        nodefactory.create_node_from_config(config)
        # print(nodefactory.name2objs.keys())
        self._service_group = nodefactory["service_group"]
        self._super_group = nodefactory["super_group"]
        self._cross_group = nodefactory["cross_group"]
        self._center = nodefactory["center"]
        if not isinstance(self._center, list):
            self._center = [self._center]
        self._all_node_group = (
            self._service_group + self._super_group + self._cross_group + self._center
        )
        self._process_pool = []
        self._set_port()

    def _set_port(self):
        # 为节点分配端口
        for node in self._all_node_group:
            # 得到一个可用端口
            sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sk.bind(("127.0.0.1", 0))
            node.addr = sk.getsockname()
            node.port = sk.getsockname()[1]
            sk.close()
        # 将端口分布写出到外存，以便协议能获取
        rst = dict()
        for node in self._all_node_group:
            if node.protocol.__name__ not in rst.keys():
                rst[node.protocol.__name__] = [node.addr]
            else:
                rst[node.protocol.__name__].append(node.addr)
        file_path = os.path.join(os.path.dirname(__file__), "../resources/.addr.json")
        with open(file_path, "w") as file:
            json.dump(rst, file, indent=4)

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

    def show_service_addr(self):
        service_addrs = "; ".join([str(node.addr[1]) for node in self._service_group])
        logging.warning(
            f"all service port, choose anyone for your client:{service_addrs}"
        )
