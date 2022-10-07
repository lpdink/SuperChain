"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-07 10:52:52
Description: 
"""
from nodes.base import Base
from framework import factory
from common import config


@factory("nodes.Service")
class Service(Base):
    def __init__(self, addr=None, config=config) -> None:
        super().__init__(addr, config)
