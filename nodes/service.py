"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-13 09:11:14
Description: 业务链节点
"""
import json

from nodes.base import Base
from utils import value_dispatch, Msg, sha256
from framework import factory
from common import config, logging


@factory("nodes.Service")
class Service(Base):
    def __init__(self, addr=None, config=config) -> None:
        super().__init__(addr, config)
        self.client2cross = dict()
        self.cross2client = dict()
        self.log_repo = dict()  # 日志的存储位置
        self.commit2flag = dict()  # 标识已上链的节点数量，用于判断日志是否在全部节点上链

    @value_dispatch
    def handle_msg(self, type, msg, addr):
        logging.error(f"unexpected msg type:{type} with msg:{msg}, please check.")
        return False

    @handle_msg.register(Msg.INIT_SESSION_REQUEST)
    def _(self, type, msg, addr):
        # 转发包体
        if addr in self.client2cross.keys():
            cross = self.client2cross[addr]
        else:
            cross = self.cross
            self.client2cross[addr] = cross
            self.cross2client[cross] = addr
        self.rpc.send(msg, cross)
        logging.info(
            f"service node {self.addr} handle msg {type} forward package to cross {cross}"
        )

    @handle_msg.register(Msg.INIT_SEESION_RESPONSE)
    def _(self, type, msg, addr):
        client_addr = msg.get("client-addr", None)
        if client_addr is None:
            logging.error(f"{type} have not client-addr section. Handle msg failed.")
        self.rpc.send(msg, tuple(client_addr))

    @handle_msg.register(Msg.CLIENT_COMMIT_LOG_REQUEST)
    def _(self, type, msg, addr):
        """
        处理来自客户端的日志上链请求:
        将日志上链
        向其他业务链节点发起SERVICE_COMMIT_LOG_REQUEST
        """
        # msg["client_id"]类似["127.0.0.1", 23456],这里将其str为"127.0.0.1,23456"
        client_id, log = ",".join([str(item) for item in msg["client_id"]]), msg["log"]
        log_id = sha256(log)
        if client_id not in self.log_repo.keys():
            self.log_repo[client_id] = {log_id: log}
        else:
            self.log_repo[client_id][log_id] = log
        # log_id位置置为1，本节点已经上链该log
        commit_id = "|".join([client_id, log_id])
        self.commit2flag[commit_id] = 1
        for s_addr in self._service_addrs:
            if s_addr != self.addr:
                self.rpc.send(
                    {
                        "type": Msg.SERVICE_COMMIT_LOG_REQUEST,
                        "client_id": msg["client_id"],
                        "log": msg["log"],
                    },
                    s_addr,
                )

    @handle_msg.register(Msg.SERVICE_COMMIT_LOG_REQUEST)
    def _(self, type, msg, addr):
        """
        处理来自其他业务链节点的日志上链请求:
        将日志上链，返回SERVICE_COMMIT_LOG_RESPONSE
        """
        # msg["client_id"]类似["127.0.0.1", 23456],这里将其str为"127.0.0.1,23456"
        client_id, log = ",".join([str(item) for item in msg["client_id"]]), msg["log"]
        log_id = sha256(log)
        commit_id = "|".join([client_id, log_id])
        if client_id not in self.log_repo.keys():
            self.log_repo[client_id] = {log_id: log}
        else:
            self.log_repo[client_id][log_id] = log
        self.rpc.send(
            {"type": Msg.SERVICE_COMMIT_LOG_RESPONSE, "commit_id": commit_id}, addr
        )

    @handle_msg.register(Msg.SERVICE_COMMIT_LOG_RESPONSE)
    def _(self, type, msg, addr):
        """
        处理来自其他业务链节点的日志上链返回:
        更新该commit_id的flag
        当flag与service节点数量相等时，向client返回已上链响应。
        NOTE:
        flag在socket多进程中不会出现写冲突，
        因为只有收到本client请求的service节点能写变量flag，
        且一个service节点是单进程且单线程的
        """
        commit_id = msg["commit_id"]
        self.commit2flag[commit_id] += 1
        if self.commit2flag[commit_id] == len(self._service_addrs):
            c_addr, log_id = commit_id.split("|")
            addr, port = c_addr.split(",")
            c_addr = (addr, int(port))
            self.rpc.send(
                {
                    "type": Msg.CLIENT_COMMIT_LOG_RESPONSE,
                    "client_id": c_addr,
                    "log_id": log_id,
                },
                c_addr,
            )
            self.commit2flag.pop(commit_id)
            logging.info(f"client {c_addr} log {log_id} commited")
