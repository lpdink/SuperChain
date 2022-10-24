"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-24 06:12:08
Description: 监管链节点
"""
from common import KeyManager, config, logging
from framework import factory
from nodes.base import Base
from utils import Msg, sha256, value_dispatch


@factory("nodes.Super")
class Super(Base):
    def __init__(self, addr=None, config=config) -> None:
        super().__init__(addr, config)
        self.to_supervise_pool = dict()

    @value_dispatch
    def handle_msg(self, type, msg, addr):
        logging.error(f"unexpected msg type:{type} with msg:{msg}, please check.")
        return False

    @handle_msg.register(Msg.SERVICE_FORWARD_TO_SUPER)
    def _(self, type, msg, addr):
        client_id = tuple(msg["client_id"])
        encrypt_log = bytes.fromhex(msg["log"])
        # 缓冲待监察信息
        if client_id not in self.to_supervise_pool.keys():
            self.to_supervise_pool[client_id] = [encrypt_log]
        else:
            self.to_supervise_pool[client_id].append(encrypt_log)
        # 向密钥中心查询该client_id的key
        self.rpc.send(
            {"type": Msg.SUPER_SEARCH_KEY_REQUEST, "client_id": client_id}, self.center
        )

    @handle_msg.register(Msg.SUPER_SEARCH_KEY_RESPONSE)
    def _(self, type, msg, addr):
        client_id = tuple(msg["client_id"])
        key = bytes.fromhex(msg["key"])
        # NOTE:如果同一client可以拥有多个key，此处依然存在key过期问题。
        encrypt_logs = self.to_supervise_pool[client_id]
        for encrypt_log in encrypt_logs:
            # NOTE:log_id的计算与service耦合。
            log_id = sha256(encrypt_log.hex())
            log = KeyManager.decrypt(encrypt_log, key).decode("utf-8")
            is_risky = self.supervise(log)
            logging.info(f"[Super] supervise log:{log}, is risky? {is_risky}")
            if is_risky:
                logging.warning(f"log {log} is risky! Prepare to delete it.")
                self.rpc.send(
                    {
                        "type": Msg.SUPER_DELETE_TO_SERVICE,
                        "client_id": client_id,
                        "log_id": log_id,
                    },
                    self.cross,
                )

    def supervise(self, msg):
        # 返回信息是否敏感
        # 对于多种监察策略，继承super类，分别实现各自的supervise方法即可。
        return "panda" in msg
