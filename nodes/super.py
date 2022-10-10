"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-10 09:15:04
Description: 监管链节点
"""
from nodes.base import Base
from framework import factory
from common import config, logging, KeyManager
from utils import Msg, value_dispatch


@factory("nodes.Super")
class Super(Base):
    def __init__(self, addr=None, config=config) -> None:
        super().__init__(addr, config)
        self.client2key = {}

    @value_dispatch
    def handle_msg(self, type, msg, addr):
        logging.error(f"unexpected msg type:{type} with msg:{msg}, please check.")
        return False

    @handle_msg.register(Msg.INIT_SESSION_REQUEST)
    def _(self, type, msg, addr):
        pub_key = msg.get("client-pub", None)
        client_addr = msg.get("client-addr", None)
        if pub_key is None:
            logging.error(f"{type} have not client-pub section. Handle msg failed.")
            return False
        if client_addr is None:
            logging.error(f"{type} have not client-addr section. Handle msg failed.")
        key = KeyManager.generate_key()
        encrypt_key = KeyManager.encrypt_with_pub(key, pub_key)
        self.rpc.send(
            {
                "type": Msg.INIT_SEESION_RESPONSE,
                "encrypt-key": encrypt_key.hex(),  # to string, 以使其能被json化
                "client-addr": client_addr,
            },
            addr,
        )
        self.client2key[tuple(client_addr)] = key
        logging.info(f"super {self.addr} generate key {key}")
