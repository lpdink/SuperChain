"""
Author: lpdink
Date: 2022-10-13 05:38:47
LastEditors: lpdink
LastEditTime: 2022-10-24 04:09:24
Description: TDD：提交日志(上链)的测试程序:
1. 客户端发送msg，包含log包体给随机的service节点
2. service节点将msg发送给其他service节点
"""
from common import get_config, logging
from common.KeyManager import KeyManager
from cs import Client, Server
from protocols import *
from utils import sha256

if __name__ == "__main__":
    msg = "唯一的归宿是安宁。panda"
    obj_config = get_config("./resources/node.json")
    server = Server(obj_config)
    server.run(behind=False)
    client = Client()
    session = client.init_session(server.service.addr)
    client_id, log_id = client.commit(msg)
    # log_id是加密log的sha256摘要，但不可在本地复现，因为encrypt算法是不确定的.
    client.exit()
    # server.shut_down()
