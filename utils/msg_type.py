"""
Author: lpdink
Date: 2022-10-08 09:04:09
LastEditors: lpdink
LastEditTime: 2022-10-24 03:14:42
Description: 定义各类节点能发送的消息类型
"""


class Msg:
    INIT_SESSION_REQUEST = 1001
    INIT_SEESION_RESPONSE = 1002
    CLIENT_COMMIT_LOG_REQUEST = 1003
    CLIENT_COMMIT_LOG_RESPONSE = 1004
    SERVICE_COMMIT_LOG_REQUEST = 1005
    SERVICE_COMMIT_LOG_RESPONSE = 1006
    SERVICE_FORWARD_TO_SUPER = 1007
    SUPER_DELETE_TO_SERVICE = 1008
    SUPER_SEARCH_KEY_REQUEST = 1009
    SUPER_SEARCH_KEY_RESPONSE = 1010



if __name__ == "__main__":
    import json

    dic = {"test": Msg.INIT_SEESION_RESPONSE}
    test = json.dumps(dic)
    breakpoint()
# class ClientMsg(Enum):
#     INIT_SESSION = auto()


# class ServiceMsg(Enum):
#     INIT_SESSION = auto()

# class CrossMsg(Enum):
#     RE

# class SuperMsg(Enum):
