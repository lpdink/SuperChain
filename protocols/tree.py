import json
import socket
from common import KeyManager, config, logging
from utils import *

from .base import BaseProtocol
from .node import nodefactory
from .consensus import ConsensusNodeInit, Package, ConsensusNodePool

@nodefactory("protocols.TreeConsensusProtocol")
class TreeConsensusProtocol(BaseProtocol):
    def __init__(self, init_status: ConsensusNodeInit) -> None:
        self.init_status = init_status
        self.batch_size = config.consensus.batch_size
        self.package_size = config.consensus.package_size
        self.package = None
        self.pool = ConsensusNodePool()
        # self.tmp_idx = 0
        if init_status.role == RoleType.POSTBOX:
            self.request_pool = []  # 需求池，攒够一个batch后放入batch_pool

    @value_dispatch
    def handle_msg(self, type, msg, addr):
        logging.error(f"unexpected msg type:{type} with msg:{msg}, please check.")
        return False

    # 邮箱将每个request暂存，到batch_size个时发送给leader
    @handle_msg.register(ConsensusMsg.USER_REQUEST)
    @check_role(RoleType.POSTBOX)
    def packup_request(self, type, msg, addr):
        data = msg.get("data", None)
        # logging.warning(self.tmp_idx)
        # self.tmp_idx+=1
        if data is None:
            logging.error(f"user request without key 'data', please check!:{msg}")
            exit()
        self.request_pool.append(data)
        if len(self.request_pool) >= self.batch_size:
            rst_msg = {
                "type": ConsensusMsg.leader.BEGIN_ANNOUNCEMENT,
                "client": msg["client"],
                "data": self.request_pool[: self.batch_size],
            }
            self.sendto(rst_msg, self.init_status.leader.addr)
            self.request_pool = self.request_pool[self.batch_size :]

    def send_package(self, package: Package, p_256, addr):
        # p_256 = package.get_sha256()
        for bx, batch in enumerate(package):
            rst_msg = {
                "type": ConsensusMsg.leader.ANNOUNCEMENT,
                "data": batch,
                "bx": bx,
                "sha256": p_256,
            }
            self.sendto(rst_msg, addr)

    @handle_msg.register(ConsensusMsg.leader.BEGIN_ANNOUNCEMENT)
    @check_role(RoleType.LEADER)
    def announcement(self, type, msg, addr):
        batch_data = msg["data"]
        self.client_addr = msg["client"]
        self.pool.batch_pool.append(batch_data)
        # if len(self.pool.package_pool)<self.package_size:
        #     if self.pool.package_pool[-1].
        if len(self.pool.batch_pool) >= self.package_size:
            package = Package(self.pool.batch_pool[: self.package_size])
            self.pool.batch_pool = self.pool.batch_pool[self.package_size :]
            p_256 = package.get_sha256()
            self.pool.package_pool[p_256] = package
            self.send_package(package, p_256, self.init_status.left.addr)
            self.send_package(package, p_256, self.init_status.right.addr)
            logging.info("announcement end")

    @handle_msg.register(ConsensusMsg.leader.ANNOUNCEMENT)
    @check_role(RoleType.FOLLOWER)
    def commitment(self, type, msg, addr):
        data = msg["data"]
        bx = msg["bx"]
        sha256 = msg["sha256"]
        sha256_bytes = bytes.fromhex(sha256)
        # 上链
        if sha256 not in self.pool.package_pool.keys():
            package = Package.regain_package(sha256)
            self.pool.package_pool[sha256] = package
        package = self.pool.package_pool[sha256]
        package.put_in_with_bx(data, bx)

        if package.regain_done():
            # 非叶节点直接转发
            if self.init_status.left is not None and self.init_status.right is not None:
                # self.sendto(msg, self.init_status.left.addr)
                # self.sendto(msg, self.init_status.right.addr)
                self.send_package(package, sha256, self.init_status.left.addr)
                self.send_package(package, sha256, self.init_status.right.addr)
            else:
                # 叶子节点对msg进行审查，决定是否参与共识.
                promise_x, promise_rsum = None, None
                self.pool.commit_status_pool[sha256] = None
                valid = 1
                rst_msg = {
                    "type": ConsensusMsg.follower.COMMITMENT,
                    "promise_x": promise_x,
                    "promise_rsum": promise_rsum,
                    "valid": valid,
                    "sha256": sha256,
                }
                self.sendto(rst_msg, addr)
            logging.info("comment end")

    @handle_msg.register(ConsensusMsg.follower.COMMITMENT)
    @check_role(RoleType.FOLLOWER, RoleType.LEADER)
    def aggregate_commit(self, type, msg, addr):
        promise_x, promise_rsum = msg["promise_x"], msg["promise_rsum"]
        sha256 = msg["sha256"]
        sha256_bytes = bytes.fromhex(sha256)
        # 保存来自左右节点的承诺,对leader和中间follower都一样
        if tuple(addr) == tuple(self.init_status.left.addr):
            self.pool.left_promise_pool[sha256] = (promise_x, promise_rsum)
        elif tuple(addr) == tuple(self.init_status.right.addr):
            # self.right_promise_dict[sha256] = promise
            self.pool.right_promise_pool[sha256] = (promise_x, promise_rsum)
        else:
            logging.error("Parent node receive msg from wrong node!")
            exit()
        # 只有同时收到左右两个节点的回复(承诺体可能为None)，才开启聚合
        if (
            sha256 in self.pool.left_promise_pool.keys()
            and sha256 in self.pool.right_promise_pool.keys()
        ):
            # parent 节点审查
            if self.is_valid(self.pool.package_pool[sha256]):
                # leader节点也进行了签名
                promise_x, promise_rsum = None, None
                valid = 1
            else:
                promise_x, promise_rsum = None, None
                valid = 0
                self.pool.commit_status_pool[sha256] = None
            if self.init_status.role == RoleType.FOLLOWER:
                rst_msg = {
                    "type": ConsensusMsg.follower.COMMITMENT,
                    "promise_x": promise_x,
                    "promise_rsum": promise_rsum,
                    "valid": valid,
                    "sha256": sha256,
                }
                self.sendto(rst_msg, self.init_status.parent.addr)
            elif self.init_status.role == RoleType.LEADER:
                # leader节点生成challange。
                rst_msg = {
                    "type": ConsensusMsg.leader.CHALLANGE,
                    "flag_ai": None,
                    "flag_ki": None,
                    "challenge": None,
                    "sha256": sha256,
                }
                self.sendto(rst_msg, self.init_status.left.addr)
                self.sendto(rst_msg, self.init_status.right.addr)

            else:
                raise RuntimeError("This line should not be exec!")
            logging.info("aggregate_commit")

    @handle_msg.register(ConsensusMsg.leader.CHALLANGE)
    @check_role(RoleType.FOLLOWER)
    def response(self, type, msg, addr):
        challenge = msg["challenge"]
        sha256 = msg["sha256"]
        if self.init_status.left is not None and self.init_status.right is not None:
            self.sendto(msg, self.init_status.left.addr)
            self.sendto(msg, self.init_status.right.addr)
        else:
            rst_msg = {
                "type": ConsensusMsg.follower.RESPONSE,
                "sha256": sha256,
                "ssum": None,
            }
            self.sendto(rst_msg, addr)
        logging.info("response")

    @handle_msg.register(ConsensusMsg.follower.RESPONSE)
    @check_role(RoleType.LEADER, RoleType.FOLLOWER)
    def aggregate_response(self, type, msg, addr):
        sha256 = msg["sha256"]
        ssum = msg["ssum"]
        if tuple(addr) == self.init_status.left.addr:
            self.pool.left_response_pool[sha256] = ssum
        elif tuple(addr) == self.init_status.right.addr:
            self.pool.right_response_pool[sha256] = ssum
        else:
            logging.error("Parent node receive msg from wrong node!")

        if (
            sha256 in self.pool.left_response_pool.keys()
            and sha256 in self.pool.right_response_pool.keys()
        ):
            if self.init_status.role == RoleType.FOLLOWER:
                rst_msg = {
                    "type": ConsensusMsg.follower.RESPONSE,
                    "sha256": sha256,
                    "ssum": None,
                }
                self.sendto(rst_msg, self.init_status.parent.addr)
            elif self.init_status.role == RoleType.LEADER:
                sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sk.bind(("127.0.0.1", 0))
                sk.sendto(b"all path done.", tuple(self.client_addr))
                sk.close()
                # logging.warning("all path done.")
            else:
                raise RuntimeError("This line should not be exec!")
            logging.info("aggregate_response")

    def is_valid(self, msgs):
        return True
