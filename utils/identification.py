# 身份鉴定装饰器，符合特定身份时执行函数，否则直接返回
# usage:
# @check_role(role, role2...)
from common import logging


def check_role(*role):
    def decorate(func):
        def inside(self, *args):
            if self.role not in role:
                logging.warning(
                    f"node {self.addr} role check failed, {self.role} not in {role}. command will not exec."
                )
                # print(f"node {self.addr} role check failed, {self.role} not in {role}. command will not exec.")
                return None
            else:
                rst = func(self, *args)
                return rst

        return inside

    return decorate


# 以下是check_role的测试.
# class Node:
#     def __init__(self) -> None:
#         self.role = 1001
#         self.addr = "192.168.0.1"

#     @check_role(1002, 1003)
#     def test(self, params):
#         print(f"test function called with {params}")
#         print(f"addr:{self.addr} role:{self.role}")
#         return params

#     def test2(self):
#         def get_some(self):
#             print(f"get some addr:{self.addr}")
#         get_some(self)

# if __name__=="__main__":
#     node = Node()
#     node.test(12)
