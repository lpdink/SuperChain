"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-07 09:05:49
Description: 监管链节点
"""
from nodes.base import Base
from framework import factory
from common import config


@factory("nodes.Super")
class Super(Base):
    def __init__(self, addr=None, config=config) -> None:
        super().__init__(addr, config)
        self.key_dict = {}
