import json
import os
import random
import socket
import time
from multiprocessing import Process

from common import logging
from protocols import nodefactory
from utils import RoleType


class ConsensusServer:
    _instance = None

    def __new__(cls, config, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self, config) -> None:
        nodefactory.create_node_from_config(config)
        self.consensus_group = nodefactory["consensus_group"]
        # breakpoint()
        assert len(self.consensus_group) >= 4, "consensus node nums must >=4 !"
        assert len(self.consensus_group) % 2 == 0, "consensus node nums must be even!"
        self._process_pool = []
        self._set_port()
        self._set_tree()

    def _set_port(self):
        # 为节点分配端口
        for node in self.consensus_group:
            # 得到一个可用端口
            sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sk.bind(("127.0.0.1", 0))
            node.addr = sk.getsockname()
            node.port = sk.getsockname()[1]
            sk.close()
        # 将端口分布写出到外存，以便协议能获取
        rst = dict()
        for node in self.consensus_group:
            if node.protocol.__name__ not in rst.keys():
                rst[node.protocol.__name__] = [node.addr]
            else:
                rst[node.protocol.__name__].append(node.addr)
        file_path = os.path.join(os.path.dirname(__file__), "../resources/.addr.json")
        with open(file_path, "w") as file:
            json.dump(rst, file, indent=4)

    def _set_tree(self):
        self.consensus_group[0].role = RoleType.POSTBOX
        self.consensus_group[0].leader = self.consensus_group[1]
        self.consensus_group[0].parent = None
        self.consensus_group[0].left = None
        self.consensus_group[0].right = None
        tree_nodes = self.consensus_group[1:]  # 浅拷贝正是我们需要的
        for idx, node in enumerate(tree_nodes):
            left_idx = 2 * idx + 1
            right_idx = 2 * idx + 2
            parent_idx = int((idx - 1) / 2)
            node.left = tree_nodes[left_idx] if left_idx < len(tree_nodes) else None
            node.right = tree_nodes[right_idx] if right_idx < len(tree_nodes) else None
            node.parent = tree_nodes[parent_idx]
            node.leader = tree_nodes[0]
            if idx == 0:
                node.role = RoleType.LEADER
                node.parent = None
            else:
                node.role = RoleType.FOLLOWER

    def run(self, behind=False):
        for node in self.consensus_group:
            node_process = Process(target=node.run, daemon=behind)
            self._process_pool.append(node_process)
        for process in self._process_pool:
            process.start()
        logging.info("Server begin running.")

    def shut_down(self):
        for process in self._process_pool:
            process.terminate()
        logging.info("Server shutdown.")

    def show_postbox_addr(self):
        assert (
            self.consensus_group[0].role == RoleType.POSTBOX
        ), "group idx 0 should be POSTBOX."
        logging.warning(f"POSTBOX addr is {self.consensus_group[0].addr}")
