from nodes.base import Base
from framework import factory
from common import config


@factory("nodes.Service")
class Service(Base):
    def __init__(self, addr=None, config=config) -> None:
        super().__init__(addr, config)
