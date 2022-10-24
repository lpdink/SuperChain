"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-20 09:25:41
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
        self.client2key = dict()
        self.to_supervise_pool=dict()

    @value_dispatch
    def handle_msg(self, type, msg, addr):
        logging.error(f"unexpected msg type:{type} with msg:{msg}, please check.")
        return False

    @handle_msg.register(Msg.SERVICE_FORWARD_TO_SUPER)
    def _(self, type, msg, addr):
        client_id = tuple(msg["client_id"])
        encrypt_log = bytes.fromhex(msg["log"])
        # 如果找不到key，加入待审查池，等待其他super的key
        # 在实际工程中，应该设置过期时间，以避免存储过大的待审查内容。
        if client_id not in self.client2key.keys():
            logging.warning(f"[Super] client_id {client_id} not in client2key, waiting for other super's key.")
            if client_id not in self.to_supervise_pool.keys():
                self.to_supervise_pool[client_id] = [encrypt_log]
            else:
                self.to_supervise_pool[client_id].append(encrypt_log)
            return
        key = self.client2key[client_id]
        log = KeyManager.decrypt(encrypt_log,key)
        logging.info(f"[Super] receive supervised log:{log}")