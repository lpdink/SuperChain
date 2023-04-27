import json
import time
import socket
from common import KeyManager, config, logging
from utils import *

from .base import BaseProtocol
from .node import nodefactory
from .consensus import ConsensusNodeInit, ConsensusNodePool, Package

class NetworkNodeInit(ConsensusNodeInit):
    def __init__(self, role, public_key=None, private_key=None, addr2node=None, nodes=None, leader=None) -> None:
        super().__init__(role, public_key, private_key, None, None, None, None, leader)
        self.addr2node = addr2node
        self.nodes = nodes

@nodefactory("protocols.NetworkProtocol")
class NetworkProtocol(BaseProtocol):
    def __init__(self, init_status: NetworkNodeInit) -> None:
        self.init_status = init_status
        self.batch_size = config.consensus.batch_size
        self.package_size = config.consensus.package_size
        self.package = None
        self.agree_pool = dict()
        self.reponse_pool = dict()
        self.pool = ConsensusNodePool()
        self.time_pool = dict()
        self.max_tps = -1
        self.total_tps = 0
        self.finish_nums = 0
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
        if len(self.pool.batch_pool) >= self.package_size:
            package = Package(self.pool.batch_pool[: self.package_size])
            self.pool.batch_pool = self.pool.batch_pool[self.package_size :]
            p_256 = package.get_sha256()
            self.time_pool[p_256] = time.perf_counter()
            self.pool.package_pool[p_256] = package
            for node in self.init_status.nodes:
                if node.addr!=self.addr:
                    self.send_package(package, p_256, node.addr)

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
            msg = "Agree"
            sign = self.init_status.private_key.sign(msg)
            rst_msg = {
                "type": ConsensusMsg.follower.COMMITMENT,
                "sign":sign,
                "sha256": sha256,
            }
            for node in self.init_status.nodes:
                if node.addr!=self.addr:
                    self.sendto(rst_msg, node.addr)

    @handle_msg.register(ConsensusMsg.follower.COMMITMENT)
    @check_role(RoleType.FOLLOWER, RoleType.LEADER)
    def aggregate_commit(self, type, msg, addr):
        sign = msg["sign"]
        sha256 = msg["sha256"]
        sha256_bytes = bytes.fromhex(sha256)
        signed_node = self.init_status.addr2node[addr]
        signed_node.init_status.public_key.verify(sign, "Agree")
        if self.init_status.role == RoleType.LEADER:
            # signed_node.init_status.public_key.verify(sign, "Agree")
            if sha256 not in self.agree_pool.keys():
                self.agree_pool[sha256] = 1
            else:
                self.agree_pool[sha256]+=1
            if self.agree_pool[sha256]>=len(self.init_status.nodes)//3*2:
                self.agree_pool[sha256]*=-10
                msg = "confirm"
                sign = self.init_status.private_key.sign(msg)
                rst_msg = {
                        "type": ConsensusMsg.leader.CHALLANGE,
                        "sha256": sha256,
                        "sign":sign
                    }
                for node in self.init_status.nodes:
                    if node.addr!=self.addr:
                        self.sendto(rst_msg, node.addr)

        

    @handle_msg.register(ConsensusMsg.leader.CHALLANGE)
    @check_role(RoleType.FOLLOWER)
    def response(self, type, msg, addr):
        sha256 = msg["sha256"]
        sign = msg["sign"]
        signed_node = self.init_status.addr2node[addr]
        signed_node.init_status.public_key.verify(sign, "confirm")
        rst_msg = {
            "type": ConsensusMsg.follower.RESPONSE,
            "sha256": sha256,
        }
        self.sendto(rst_msg, addr)

    @handle_msg.register(ConsensusMsg.follower.RESPONSE)
    @check_role(RoleType.LEADER)
    def aggregate_response(self, type, msg, addr):
        sha256 = msg["sha256"]
        if sha256 not in self.reponse_pool.keys():
            self.reponse_pool[sha256] = 1
        else:
            self.reponse_pool[sha256]+=1
        if self.reponse_pool[sha256]>=len(self.init_status.nodes)//3*2:
            self.reponse_pool[sha256]*=-10
            # self.sendto(msg, self.client_addr)
            sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sk.bind(("127.0.0.1", 0))
            sk.sendto(b"all path done.", tuple(self.client_addr))
            sk.close()
            end = time.perf_counter()
            duration = end - self.time_pool[sha256]
            tps = self.package_size*self.batch_size/duration
            self.max_tps = max(tps, self.max_tps)
            self.total_tps+=tps
            self.finish_nums+=1
            self.avg_tps = self.total_tps/self.finish_nums
            logging.warning(f"tps: {tps} max_tps:{self.max_tps} avg_tps:{self.avg_tps}")
            
    def is_valid(self, msgs):
        return True

    
    