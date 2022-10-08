"""
Author: lpdink
Date: 2022-10-07 09:06:46
LastEditors: lpdink
LastEditTime: 2022-10-08 09:43:21
Description: 客户端创建的请求
"""
from common import KeyManager, logging
from framework import Rpc
from utils import Msg


class Session:
    def __init__(self, client_addr, server_addr) -> None:
        self.c_addr = client_addr
        self.c_rpc = Rpc(self.c_addr)
        self.s_addr = server_addr
        self.pub, self.priv = KeyManager.generate_pair()
        self.key = None
        # 发送请求
        self._sent_pair_key_to_server()
        # 开始监听
        response, _ = self._recv()
        if isinstance(response, dict) and response["type"] == Msg.INIT_SEESION_RESPONSE:
            self.key = response["key"]

    def _sent_pair_key_to_server(self):
        self.c_rpc.send(
            {
                "type": Msg.INIT_SESSION_REQUEST,
                "client-pub": self.pub,
                "client-id": self.c_rpc.addr,
            },
            self.s_addr,
        )

    def _recv(self):
        while True:
            try:
                try:
                    data, addr = self.rpc.recv()
                except:
                    data, addr = {}, None
                if addr is not None:
                    return data, addr
            except KeyboardInterrupt:
                self.rpc.close()

