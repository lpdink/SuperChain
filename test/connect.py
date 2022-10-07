"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-07 10:53:10
Description: 测试工厂创建对象，节点之间彼此链接并收发包的基础功能
"""
from framework import factory, Rpc
from nodes import Service
from common import get_config, logging
from multiprocessing import Process

# 模拟客户端进程，向每个节点发送msg


def send_package_to_all_node(port_list):
    client = Rpc()
    msg = "I am ping package. "
    for index, port in enumerate(port_list):
        target_addr = ("127.0.0.1", port)
        client.send({"msg": f"{msg} index: {index}"}, target_addr)


def main():
    # 从config中创造node对象
    obj_config = get_config("../resources/node.json")
    factory.create_obj_from_config(obj_config)

    service_node_group = factory["service_group"]

    # 打印占用端口
    port_list = []
    for node in service_node_group:
        node: Service = node
        port_list.append(node.port)
    logging.info(f"following ports are binded:{port_list}")

    process_pool = []
    # 创建节点进程(server)
    for node in service_node_group:
        node: Service = node
        process = Process(target=node.run)
        process_pool.append(process)

    client_process = Process(target=send_package_to_all_node, args=(port_list,))
    process_pool.append(client_process)

    # 开始进程
    for process in process_pool:
        process.start()
    # 结束
    for process in process_pool:
        process.join()


if __name__ == "__main__":
    main()
