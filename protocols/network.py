import json

from common import KeyManager, config, logging
from utils import *

from .base import BaseProtocol
from .node import nodefactory
from .consensus import ConsensusNodeInit

@nodefactory("protocols.NetworkProtocol")
class NetworkProtocol(BaseProtocol):
    def __init__(self, init_status) -> None:
        super().__init__()

    @value_dispatch
    def handle_msg(self, type, msg, addr):
        logging.error(f"unexpected msg type:{type} with msg:{msg}, please check.")
        return False
    
    