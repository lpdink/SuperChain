"""
Author: lpdink
Date: 2022-10-07 02:00:21
LastEditors: lpdink
LastEditTime: 2022-10-10 08:35:33
Description: TDD:密钥分发的测试程序，将打印客户端与参与session的super节点的密钥。
"""
from common import get_config, logging
from cs import Client, Server
from nodes import *

if __name__ == "__main__":
    obj_config = get_config("./resources/node.json")
    server = Server(obj_config)
    server.run(behind=True)
    client = Client()
    # 本session实际上是由client与super进行的，但是对client来说，监管节点是不可见的。
    # 故client选取了server提供的一个随机service节点
    # client.bind(server.service.addr)
    session = client.init_session(server.service.addr)
    logging.warning(f"rsa key from client:{client.key}")
    client.stop_session()
    client.exit()
    server.shut_down()
