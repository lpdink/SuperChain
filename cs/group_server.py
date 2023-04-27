from .consensus_server import ConsensusServer
from cryptography.hazmat.primitives.asymmetric import ec
import json
import os
import random
import socket
import time
from multiprocessing import Process

from common import logging
from protocols import NetworkNodeInit, nodefactory
from utils import RoleType, create_keypair, pubkey_gen_from_hex, sha256_bytes

class PrivateKey:
    def __init__(self, pri_key) -> None:
        self.pri_key = pri_key

    def sign(self, msg):
        # return ""
        if not isinstance(msg, bytes):
            msg = msg.encode()
        rst = self.pri_key.sign(msg, ec.ECDSA(ec.hashes.SHA256()))
        if isinstance(rst, bytes):
            rst = rst.hex()
        return rst

class PublicKey:
    def __init__(self, pub_key) -> None:
        self.pub_key = pub_key

    def verify(self, sign, msg):
        # return True
        if not isinstance(msg, bytes):
            msg = msg.encode()
        if not isinstance(sign, bytes):
            sign = bytes.fromhex(sign)
        self.pub_key.verify(sign, msg, ec.ECDSA(ec.hashes.SHA256()))
        return True

class Key:
    def __init__(self) -> None:
        private_key = ec.generate_private_key(ec.SECP256K1())
        public_key = private_key.public_key()
        self.pub_key = PublicKey(public_key)
        self.pri_key = PrivateKey(private_key)

class GroupServer(ConsensusServer):
    def __init__(self, config) -> None:
        nodefactory.create_node_from_config(config)
        self.consensus_group = nodefactory["consensus_group"]
        # breakpoint()
        assert len(self.consensus_group) >= 4, "consensus node nums must >=4 !"
        self._process_pool = []
        self._set_port()
        self._set_nodes()

    def _set_nodes(self):
        post_box_init = NetworkNodeInit(
            role=RoleType.POSTBOX, leader=self.consensus_group[1]
        )
        self.consensus_group[0].init_status = post_box_init
        nodes = self.consensus_group[1:]  # 浅拷贝正是我们需要的
        pub_keys, priv_keys = self.gen_keys(len(nodes))
        addr2node = {node.addr:node for node in nodes}
        for idx, node in enumerate(nodes):
            node_leader = nodes[0]
            if idx == 0:
                node_role = RoleType.LEADER
            else:
                node_role = RoleType.FOLLOWER
            node_status = NetworkNodeInit(
                node_role, pub_keys[idx], priv_keys[idx], addr2node=addr2node, nodes=nodes, leader=node_leader
            )
            node.init_status = node_status

    def gen_keys(self, n):
        keys = [Key() for _ in range(n)]
        return [key.pub_key for key in keys], [key.pri_key for key in keys]
