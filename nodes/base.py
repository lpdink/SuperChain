"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-07 03:33:26
Description: 
"""
from framework import Rpc, factory
from common import config, logging


@factory("nodes.Base")
class Base:
    def __init__(self, addr=None, config=config) -> None:
        print(config)
        self.rpc = Rpc(addr, config.connection)

    @property
    def port(self):
        return self.rpc.port

    @property
    def addr(self):
        return self.rpc.addr

    # 持续接收，打印接收到的数据
    def run(self):
        while True:
            try:
                try:
                    data, addr = self.rpc.recv()
                except:
                    data, addr = {}, None
                if addr is not None:
                    logging.info(f"{self.rpc.addr} receive {data} from addr {addr}")
            except KeyboardInterrupt:
                self.rpc.close()


if __name__ == "__main__":
    base = Base()
    base.run()
