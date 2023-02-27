"""
Author: lpdink
Date: 2022-10-28 08:48:13
LastEditors: lpdink
LastEditTime: 2022-10-28 10:41:46
Description: 
"""
import asyncio
import random
import sys
import json

from common import logging, config
from utils import ConsensusMsg


class Node:
    def __init__(self, protocol) -> None:
        self.protocol = protocol

    def run(self):
        asyncio.run(self.run_node())

    async def run_node(self):
        loop = asyncio.get_running_loop()
        transport, protocol_obj = await loop.create_datagram_endpoint(
            lambda: self.protocol(), local_addr=self.addr
        )
        msg = {"type":ConsensusMsg.follower.RESET}
        msg = json.dumps(msg).encode("utf-8")
        while True:
            try:
                protocol_obj.reset = True
                await asyncio.sleep(config.consensus.view_conversion_time)  # 视图转换时间
                transport.sendto(msg, tuple(self.addr))
            except:
                transport.close()


class NodeFactory:
    """生产不同协议类型的node"""

    def __init__(self) -> None:
        self.name2protocol = dict()
        self.protocol2name = dict()
        self.name2objs = dict()

    def __call__(self, name):
        def register(protocol):
            if name not in self.name2protocol:
                self.name2protocol[name] = protocol
            else:
                logging.error(f"protocol name {name} already registered!")
                sys.exit(-1)
            if protocol not in self.protocol2name:
                self.protocol2name[protocol] = name
            else:
                logging.error(
                    f"protocol already registered with name {self.protocol2name[protocol]}!"
                )
                sys.exit(-1)
            return protocol

        return register

    def __getitem__(self, key):
        return self.name2objs.get(key, None)

    def create_node_from_config(self, config):
        if hasattr(config, "nodes_group"):
            for group in config.nodes_group:
                protocol = self.name2protocol.get(group.protocol, None)
                if protocol is None:
                    logging.warning(
                        f"no protocol in {group}, so they are not instanced"
                    )
                    continue
                node_group = [Node(protocol) for _ in range(group.nums)]
                self.name2objs[group.name] = node_group
                logging.info(f"created nodes with {group}")
        else:
            logging.error("no nodes_group in config! create nodes failed.")


nodefactory = NodeFactory()
