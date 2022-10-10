"""
Author: lpdink
Date: 2022-10-08 09:04:09
LastEditors: lpdink
LastEditTime: 2022-10-10 08:51:30
Description: 定义各类节点能发送的消息类型
"""
class Msg:
    INIT_SESSION_REQUEST=1001
    INIT_SEESION_RESPONSE=1002

if __name__=="__main__":
    import json
    dic = {"test":Msg.INIT_SEESION_RESPONSE}
    test = json.dumps(dic)
    breakpoint()
# class ClientMsg(Enum):
#     INIT_SESSION = auto()


# class ServiceMsg(Enum):
#     INIT_SESSION = auto()

# class CrossMsg(Enum):
#     RE

# class SuperMsg(Enum):

