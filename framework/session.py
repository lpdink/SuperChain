"""
Author: lpdink
Date: 2022-10-07 09:06:46
LastEditors: lpdink
LastEditTime: 2022-10-13 09:15:15
Description: 客户端创建的请求
"""
from common import KeyManager, logging
from framework import Rpc
from utils import Msg


class Session:
    def __init__(self, client_addr, server_addr) -> None:
        self.c_rpc = Rpc(client_addr)
        self.c_addr = self.c_rpc.addr
        self.s_addr = server_addr
        self.pub, self.priv = KeyManager.generate_pair()
        logging.info(f"client.session generate pair key")
        self.key = None

    def init(self):
        # 发送请求
        self._sent_pair_key_to_server()
        # 开始监听
        response, _ = self._recv()
        if isinstance(response, dict) and response["type"] == Msg.INIT_SEESION_RESPONSE:
            # self.key = response["key"]
            encrypt_key = response.get("encrypt-key", None)
            if encrypt_key is None:
                logging.error(
                    "INIT_SESSION_RESPONSE without section encrypt-key, initsession failed."
                )
                return
            self.key = KeyManager.decrypt_with_rsa(
                bytes.fromhex(encrypt_key), self.priv
            )
            logging.info(f"client receive key {self.key}")

    def _sent_pair_key_to_server(self):
        # breakpoint()
        self.c_rpc.send(
            {
                "type": Msg.INIT_SESSION_REQUEST,
                "client-pub": self.pub,
                "client-addr": tuple(self.c_rpc.addr),
            },
            self.s_addr,
        )
        logging.info(f"client.session send pair key to {self.s_addr}")

    def commit(self, log):
        log = KeyManager.encrypt(log, self.key)
        self.c_rpc.send(
            {
                "type": Msg.CLIENT_COMMIT_LOG_REQUEST,
                "log": log.hex(),  # to string, 以使其能被json化
                "client_id": self.c_addr,
            },
            self.s_addr,
        )
        data, _ = self._recv()
        if isinstance(data, dict) and data["type"] == Msg.CLIENT_COMMIT_LOG_RESPONSE:
            return data["client_id"], data["log_id"]

    def _recv(self):
        while True:
            try:
                try:
                    data, addr = self.c_rpc.recv()
                except:
                    data, addr = {}, None
                if addr is not None:
                    return data, addr
            except KeyboardInterrupt:
                self.c_rpc.close()
