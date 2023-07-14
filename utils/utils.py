"""
Author: lpdink
Date: 2022-10-13 07:23:52
LastEditors: lpdink
LastEditTime: 2022-10-13 07:25:05
Description: 
"""
import hashlib
import random
import time

HUMAN_NAMES = [
    "Tammy Henrietta",
    "Quinn Jarrectis",
]


def sha256(text: str):
    text = text.encode("utf-8")
    return hashlib.sha256(text).hexdigest()


class RoleType:
    # 共识节点类型
    POSTBOX = 100
    LEADER = 101
    FOLLOWER = 102
    VERIFIER = 103


class UserMessage:
    # 共识算法的用户消息体
    def __init__(self, src, dst, type_idx, amount, time, padding) -> None:
        self.src = src
        self.dst = dst
        self.type_idx = type_idx
        self.amount = amount
        self.time = time
        self.padding = padding

    @classmethod
    def random_msg(cls):
        # src, dst = random.choices(HUMAN_NAMES, k=2)
        src, dst = HUMAN_NAMES
        type_idx = random.randint(100, 142)
        amount = random.randint(100, 199)
        time_ = time.time().hex()
        padding = "0"*118
        return cls(src, dst, type_idx, amount, time_, padding).__dict__

    @classmethod
    def random_msgs(cls, num):
        return [UserMessage.random_msg() for _ in range(num)]


if __name__ == "__main__":
    # 一条消息120字节，udp协议最大容忍525条消息，取512为batch
    # 假设要求系统稳定运行100秒，tps5000，100秒结束时，无删除的节点内存使用增加58MB。系统使用内存上限4GB左右，能容忍约70个节点，考虑完全二叉树，不妨设节点数量为63.
    # request请求将是高频的，单一节点能在一秒内接受5000个udp包吗？可以，单一节点极限tps为10w/s
    # 要在共识达成完毕后抛弃
    tmp = UserMessage.random_msg()  # 获取tmp的记录，使用tmp.__dict__即可.
    breakpoint()
