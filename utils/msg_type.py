"""
Author: lpdink
Date: 2022-10-08 09:04:09
LastEditors: lpdink
LastEditTime: 2022-10-24 06:22:14
Description: 定义各类节点能发送的消息类型
"""


class Msg:
    INIT_SESSION_REQUEST = 1001  # 初始密钥分发请求，client(pair key)->service->cross->center
    INIT_SEESION_RESPONSE = 1002  # 初始密钥分发响应，center(key)->cross->service->client
    CLIENT_COMMIT_LOG_REQUEST = 1003  # 提交日志请求，client(log)->service
    CLIENT_COMMIT_LOG_RESPONSE = 1004  # 提交日志响应，service->client
    SERVICE_COMMIT_LOG_REQUEST = 1005  # 业务链内部日志上链请求，service->service
    SERVICE_COMMIT_LOG_RESPONSE = 1006  # 业务链内部日志上链响应，service->service
    SERVICE_FORWARD_TO_SUPER = 1007  # 业务链转发日志给监管，service->cross->super
    SUPER_DELETE_TO_SERVICE = 1008  # 监管要求删除敏感日志请求，super->corss->service
    SUPER_SEARCH_KEY_REQUEST = 1009  # 监管查询指定client-id密钥请求，super->center
    SUPER_SEARCH_KEY_RESPONSE = 1010  # 监管查询指定client-id密钥响应，center->super
    SERVICE_DELETE_TO_SERVICE = 1011  # 业务链内部删除日志请求，service->service.

class LeaderMsg:
    BEGIN_ANNOUNCEMENT=2000 # leader->leader 达到batch_size，开始共识。
    ANNOUNCEMENT = 2001 # leader-> follower
    CHALLANGE = 2002 # leader->follower

class FollowerMsg:
    COMMITMENT = 3000
    RESET = 3001

class ConsensusMsg:
    leader = LeaderMsg
    follower = FollowerMsg
    VIEW_CONVERSION = 5000
    USER_REQUEST = 5001


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
