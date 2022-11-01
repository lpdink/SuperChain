"""
Author: lpdink
Date: 2022-10-28 08:21:50
LastEditors: lpdink
LastEditTime: 2022-10-28 09:29:48
Description: 
"""
from common import KeyManager, config, logging
from utils import Msg, value_dispatch

from .base import BaseProtocol
from .node import nodefactory


@nodefactory("protocols.Center")
class CenterProtocol(BaseProtocol):
    def __init__(self) -> None:
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
        self.sendto(
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
            self.sendto(
                {
                    "type": Msg.SUPER_SEARCH_KEY_RESPONSE,
                    "key": key.hex(),
                    "client_id": client_id,
                },
                addr,
            )
        else:
            logging.warning(
                f"[center] client_id {client_id} not in self.client2key, search failed."
            )
