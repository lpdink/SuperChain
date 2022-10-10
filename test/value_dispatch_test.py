"""
Author: lpdink
Date: 2022-10-10 06:17:54
LastEditors: lpdink
LastEditTime: 2022-10-10 06:57:20
Description: 用于测试value_dispath装饰器在类中的使用。
value_dispatch装饰器无法被继承。在子类不可见(不清楚原因)，同时因为创建的闭包共享同一个registy字典。
"""
from utils import value_dispatch

class Base:
    def __init__(self) -> None:
        pass

    @value_dispatch
    # @staticmethod
    def handle_msg(self, msg_type, msg):
        print(f"this line out of expection type. with msg {msg}")

    @handle_msg.register("info")
    def _(self, msg_type, msg):
        print(f"the msg {msg} is info")

    @handle_msg.register("error")
    def _(self, msg_type, msg):
        print(f"the msg {msg} is error")
        
class SubBase(Base):
    def __init__(self) -> None:
        super().__init__()
        # breakpoint()

    @value_dispatch
    # @staticmethod
    def handle_msg(self, msg_type, msg):
        print(f"this line out of expection type. with msg {msg} in sub class")

    @handle_msg.register("info")
    def _(self, msg_type, msg):
        print(f"the msg {msg} is info in sub class")

    @handle_msg.register("error")
    def _(self, msg_type, msg):
        print(f"the msg {msg} is error in sub class")

if __name__=="__main__":
    base = Base()
    base.handle_msg("info", "no bug in your code.")
    base.handle_msg("error", "many bugs in your code!")
    sub_base = SubBase()
    sub_base.handle_msg("info", "no bug in your code.")
    sub_base.handle_msg("error", "many bugs in your code!")
