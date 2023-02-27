import json
from common import KeyManager, config, logging
from utils import (
    Msg,
    ConsensusMsg,
    sha256,
    value_dispatch,
    check_role,
    point_mul,
    create_keypair,
    int_from_hex,
    G,
)

from .base import BaseProtocol
from .node import nodefactory


class RoleType:
    LEADER = 100
    FOLLOWER = 101
    VERIFIER = 102


@nodefactory("protocols.Consensus")
class ConsensusProtocol(BaseProtocol):
    def __init__(self) -> None:
        self.role = RoleType.VERIFIER  # verifier的任务是什么？
        self.batch_size = config.consensus.batch_size
        self.request_pool = []  # 需求池，攒够一个batch后放入batch_pool
        self.batch_pool_dict = dict()  # 以batch为单位存放, sha256:data
        self.parent = None
        self.left = None
        self.left_promise_dict = dict()  # commitment阶段，左节点承诺
        self.right = None
        self.right_promise_dict = dict()  # commitment阶段，右节点承诺
        users = create_keypair(1)["users"]
        self.public_key = users[0]["publicKey"]
        self.private_key = users[0]["privateKey"]

    @value_dispatch
    def handle_msg(self, type, msg, addr):
        logging.error(f"unexpected msg type:{type} with msg:{msg}, please check.")
        return False

    # 每个request暂存，到n个时产生self消息发给自己.
    @handle_msg.register(ConsensusMsg.USER_REQUEST)
    @check_role(RoleType.LEADER)
    def packup_request(self, type, msg, addr):
        data = msg.get("data", None)
        if data is None:
            logging.error(f"user request without key 'data', please check!:{msg}")
            exit()
        self.request_pool.append(data)
        # TODO?：需要检查一下data的类型
        if len(self.request_pool) >= self.batch_size:
            rst_msg = {"type": ConsensusMsg.leader.BEGIN_ANNOUNCEMENT}
            self.sendto(rst_msg, self.addr)

    @handle_msg.register(ConsensusMsg.BEGIN_ANNOUNCEMENT)
    @check_role(RoleType.LEADER)
    def announcement(self, type, msg, addr):
        batch_data = self.request_pool[: self.batch_size]
        batch_data_256 = sha256(json.dumps(batch_data))
        rst_msg = {
            "type": ConsensusMsg.leader.ANNOUNCEMENT,
            "data": batch_data,
            "sha256": batch_data_256,
        }
        # 在发起announcement时，将request打成batch，放入batch_pool
        self.batch_pool_dict[batch_data_256] = batch_data
        self.request_pool = self.request_pool[self.batch_size :]
        self.sendto(rst_msg, self.left.addr)
        self.sendto(rst_msg, self.right.addr)

    @handle_msg.register(ConsensusMsg.leader.ANNOUNCEMENT)
    @check_role(RoleType.FOLLOWER)
    def commitment(self, type, msg, addr):
        data = msg["data"]
        sha256 = msg["sha256"]
        # 上链
        self.batch_pool_dict[sha256] = data
        # 非叶节点直接转发
        if self.left is not None and self.right is not None:
            self.sendto(msg, self.left.addr)
            self.sendto(msg, self.right.addr)
        else:
            # 叶子节点对msg进行审查，决定是否参与共识.
            if self.is_valid(data):
                # 叶子节点生成承诺，发送给父节点.
                d0 = int_from_hex(self.private_key)
                # promise:P
                promise = point_mul(G, d0)
                valid = 1
            else:
                promise = None
                valid = 0
            rst_msg = {
                "type": ConsensusMsg.follower.COMMITMENT,
                "promise": promise,
                "valid": valid,
                "sha256": sha256,
            }
            self.sendto(rst_msg, addr)

    @handle_msg.register(ConsensusMsg.follower.COMMITMENT)
    @check_role(RoleType.FOLLOWER, RoleType.LEADER)
    def aggregate_commit(self, type, msg, addr):
        promise = msg["promise"]
        sha256 = msg["sha256"]
        if self.role == RoleType.FOLLOWER:
            if tuple(addr) == tuple(self.left.addr):
                self.left_promise_dict[sha256] = promise
            elif tuple(addr) == tuple(self.right.addr):
                self.right_promise_dict[sha256] = promise
            else:
                logging.error("Follower receive msg from wrong node!")
                exit()

            # 只有同时收到左右两个节点的回复(承诺可能为None)
            if (
                sha256 in self.left_promise_dict.keys()
                and sha256 in self.right_promise_dict.keys()
            ):
                if self.is_valid(self.batch_pool_dict[sha256]):
                    # TODO 暂时不清楚怎么聚合承诺，这里有三个元组.
                    # 生成承诺，聚合，发送给父节点.
                    d0 = int_from_hex(self.private_key)
                    # promise:P
                    promise = point_mul(G, d0)  # TODO 需要修改
                    valid = 1
                else:
                    promise = None
                    valid = 0
                rst_msg = {
                    "type": ConsensusMsg.follower.COMMITMENT,
                    "promise": promise,
                    "valid": valid,
                    "sha256": sha256,
                }
                self.sendto(rst_msg, self.parent)
        elif self.role == RoleType.LEADER:
            # TODO leader节点进行challange。
            rst_msg = {"type": ConsensusMsg.leader.CHALLANGE, "body": None}
            self.sendto(rst_msg, self.left)
            self.sendto(rst_msg, self.right)
        else:
            raise RuntimeError("This line should not be exec!")

    @handle_msg.register(ConsensusMsg.leader.CHALLANGE)
    @check_role(RoleType.FOLLOWER)
    def response(self, type, msg, addr):
        pass

    # @handle_msg.register(ConsensusMsg.follower.RESET)
    # # TODO:谁应该主动发起reset？follower吗？
    # # 主动发动reset的类型，与接收reset的命令类型应该一致吗？是否需要主动和被动两种处理？
    # # @check_role()
    # def reset_self(self, type, msg, addr):
    #     # reset 应该发送给谁?
    #     self.sendto(None, None)
    #     pass

    def is_valid(self, msgs):
        return True
