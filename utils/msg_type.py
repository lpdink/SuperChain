"""
Author: lpdink
Date: 2022-10-08 09:04:09
LastEditors: lpdink
LastEditTime: 2022-10-08 09:26:03
Description: 定义各类节点能发送的消息类型
"""
from enum import Enum, auto

class Msg(Enum):
    INIT_SESSION_REQUEST=auto()
    INIT_SEESION_RESPONSE=auto()

# class ClientMsg(Enum):
#     INIT_SESSION = auto()


# class ServiceMsg(Enum):
#     INIT_SESSION = auto()

# class CrossMsg(Enum):
#     RE

# class SuperMsg(Enum):

