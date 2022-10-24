"""
Author: lpdink
Date: 2022-10-24 02:50:38
LastEditors: lpdink
LastEditTime: 2022-10-24 03:59:38
Description: 密钥中心节点，单例。
"""
from nodes.base import Base
from framework import factory
from common import config, logging, KeyManager
from utils import value_dispatch, Msg

@factory("nodes.Center")
class Center(Base):
    _instance = None

    def __new__(cls, addr=None, config=config, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        else:
            logging.error("class Center is singleton, should be instanced only once.")
            exit(-1)
        return cls._instance

    def __init__(self, addr=None, config=config) -> None:
        super().__init__(addr, config)
        self.client2key = dict()

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
        # 对于同一个client_id，保持一个key.
        client_addr = tuple(client_addr)
        if client_addr in self.client2key.keys():
            key = self.client2key[client_addr]
        else:
            key = KeyManager.generate_key()
        encrypt_key = KeyManager.encrypt_with_pub(key, pub_key)
        self.client2key[tuple(client_addr)] = key
        logging.info(f"super {self.addr} generate key {key}")
        self.rpc.send(
            {
                "type": Msg.INIT_SEESION_RESPONSE,
                "encrypt-key": encrypt_key.hex(),  # to string, 以使其能被json化
                "client-addr": client_addr,
            },
            addr,
        )

    @handle_msg.register(Msg.SUPER_SEARCH_KEY_REQUEST)
    def _(self, type, msg, addr):
        client_id = tuple(msg["client_id"])
        key = self.client2key.get(client_id, None)
        if key is not None:
            self.rpc.send({"type":Msg.SUPER_SEARCH_KEY_RESPONSE, "key":key.hex(), "client_id":client_id}, addr)
        else:
            logging.warning(f"[center] client_id {client_id} not in self.client2key, search failed.")