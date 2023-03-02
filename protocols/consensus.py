import json

from common import KeyManager, config, logging
from utils import *

from .base import BaseProtocol
from .node import nodefactory


class ConsensusNodeInit:
    """
    用于在节点构造时，传入以实例化节点协议.
    """

    def __init__(
        self,
        role,
        public_key=None,
        private_key=None,
        L=None,
        left=None,
        right=None,
        parent=None,
        leader=None,
    ) -> None:
        self.role = role
        self.left = left
        self.right = right
        self.parent = parent
        self.leader = leader
        self.public_key = public_key
        self.private_key = private_key
        self.L = L


class ConsensusCommitStatus:
    def __init__(self, x, rsum, ai, ki) -> None:
        self.x = x
        self.rsum = rsum
        self.ai = ai  # ai与msg及轮次无关，与L类似，选择固定.
        self.ki = ki

        self.left_x = None
        self.right_x = None

    def get_promise(self):
        return self.x, self.rsum


class ConsensusNodePool:
    def __init__(self) -> None:
        self.batch_pool = dict()  # 以batch为单位存放, sha256:data
        self.commit_status_pool = dict()  # 本节点commit状态
        self.left_promise_pool = dict()  # commitment阶段，左节点承诺
        self.right_promise_pool = dict()  # commitment阶段，右节点承诺
        self.left_response_pool = dict() # response阶段，左节点响应
        self.right_response_pool = dict() # response阶段，右节点响应
        self.challenge_pool = dict() # response阶段，保存challenge


@nodefactory("protocols.Consensus")
class ConsensusProtocol(BaseProtocol):
    def __init__(self, init_status: ConsensusNodeInit) -> None:
        self.init_status = init_status
        self.batch_size = config.consensus.batch_size
        self.pool = ConsensusNodePool()
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
                "client": addr,
                "data": self.request_pool[: self.batch_size],
            }
            self.sendto(rst_msg, self.init_status.leader.addr)
            self.request_pool = self.request_pool[self.batch_size :]

    @handle_msg.register(ConsensusMsg.leader.BEGIN_ANNOUNCEMENT)
    @check_role(RoleType.LEADER)
    def announcement(self, type, msg, addr):
        batch_data = msg["data"]
        self.client_addr = msg["client"]
        batch_data_256 = sha256(json.dumps(batch_data))
        rst_msg = {
            "type": ConsensusMsg.leader.ANNOUNCEMENT,
            "data": batch_data,
            "sha256": batch_data_256,
        }
        self.pool.batch_pool[batch_data_256] = batch_data
        self.sendto(rst_msg, self.init_status.left.addr)
        self.sendto(rst_msg, self.init_status.right.addr)

    def get_commit_status(self, msg, X=None, Rsum=None):
        di = int_from_hex(self.init_status.private_key)
        if not (1 <= di <= n - 1):
            raise ValueError("The secret key must be an integer in the range 1..n-1.")
        Pi = pubkey_point_gen_from_int(di)
        assert Pi is not None

        ai = int_from_bytes(sha256_bytes(self.init_status.L + bytes_from_point(Pi)))

        X = point_add(X, point_mul(Pi, ai))

        # Random ki with tagged hash
        t = xor_bytes(bytes_from_int(di), tagged_hash("BIP0340/aux", get_aux_rand()))
        ki = (
            int_from_bytes(tagged_hash("BIP0340/nonce", t + bytes_from_point(Pi) + msg))
            % n
        )
        if ki == 0:
            raise RuntimeError(
                "Failure. This happens only with negligible probability."
            )

        # Ri = ki * G
        Ri = point_mul(G, ki)
        assert Ri is not None

        # Rsum = R1 + ... + Rn
        Rsum = point_add(Rsum, Ri)
        # u["ki"] = ki
        commit_status = ConsensusCommitStatus(X, Rsum, ai, ki)
        return commit_status

    @handle_msg.register(ConsensusMsg.leader.ANNOUNCEMENT)
    @check_role(RoleType.FOLLOWER)
    def commitment(self, type, msg, addr):
        data = msg["data"]
        sha256 = msg["sha256"]
        sha256_bytes = bytes.fromhex(sha256)
        # 上链
        self.pool.batch_pool[sha256] = data
        # 非叶节点直接转发
        if self.init_status.left is not None and self.init_status.right is not None:
            self.sendto(msg, self.init_status.left.addr)
            self.sendto(msg, self.init_status.right.addr)
        else:
            # 叶子节点对msg进行审查，决定是否参与共识.
            if self.is_valid(data):
                # 密码学部分
                commit_status = self.get_commit_status(sha256_bytes, X=None, Rsum=None)
                self.pool.commit_status_pool[sha256] = commit_status
                promise_x, promise_rsum = commit_status.get_promise()
                valid = 1
            else:
                promise_x, promise_rsum = None, None
                self.pool.commit_status_pool[sha256] = None
                valid = 0
            rst_msg = {
                "type": ConsensusMsg.follower.COMMITMENT,
                "promise_x": promise_x,
                "promise_rsum": promise_rsum,
                "valid": valid,
                "sha256": sha256,
            }
            self.sendto(rst_msg, addr)

    def aggregate_commit_(self, sha256, sha256_bytes):
        left_promise_x, left_promise_rsum = self.pool.left_promise_pool[
            sha256
        ]
        right_promise_x, right_promise_rsum = self.pool.right_promise_pool[
            sha256
        ]
        # 聚合承诺
        aggragate_x = point_add(left_promise_x, right_promise_x)
        aggragete_rsum = point_add(left_promise_rsum, right_promise_rsum)
        commit_status = self.get_commit_status(
            sha256_bytes, aggragate_x, aggragete_rsum
        )
        commit_status.left_x = left_promise_x
        commit_status.right_x = right_promise_x
        self.pool.commit_status_pool[sha256] = commit_status

        promise_x = commit_status.x
        promise_rsum = commit_status.rsum
        return promise_x, promise_rsum

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
            if self.is_valid(self.pool.batch_pool[sha256]):
                # leader节点也进行了签名
                promise_x, promise_rsum = self.aggregate_commit_(sha256, sha256_bytes)
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
                flag_ai = 1 if not has_even_y(promise_x) else 0
                flag_ki = 1 if not has_even_y(promise_rsum) else 0
                challenge = (
                    int_from_bytes(
                        tagged_hash(
                            "BIP0340/challenge",
                            (
                                bytes_from_point(promise_rsum)
                                + bytes_from_point(promise_x)
                                + sha256_bytes
                            ),
                        )
                    )
                    % n
                )
                rst_msg = {
                    "type": ConsensusMsg.leader.CHALLANGE,
                    "flag_ai": flag_ai,
                    "flag_ki": flag_ki,
                    "challenge": challenge,
                    "sha256": sha256,
                }
                # leader自己反转ai, ki
                if flag_ai:
                    self.pool.commit_status_pool[sha256].ai = n - self.pool.commit_status_pool[sha256].ai
                if flag_ki:
                    self.pool.commit_status_pool[sha256].ki = n - self.pool.commit_status_pool[sha256].ki
                # leader自己保留challenge
                self.pool.challenge_pool[sha256] = challenge
                self.sendto(rst_msg, self.init_status.left.addr)
                self.sendto(rst_msg, self.init_status.right.addr)

            else:
                raise RuntimeError("This line should not be exec!")

    @handle_msg.register(ConsensusMsg.leader.CHALLANGE)
    @check_role(RoleType.FOLLOWER)
    def response(self, type, msg, addr):
        flag_ai = msg["flag_ai"]
        flag_ki = msg["flag_ki"]
        challenge = msg["challenge"]
        sha256 = msg["sha256"]
        # 这里保留challenge，是为了之后非叶节点能计算聚合.
        self.pool.challenge_pool[sha256] = challenge
        if flag_ai:
            self.pool.commit_status_pool[sha256].ai = n - self.pool.commit_status_pool[sha256].ai
        if flag_ki:
            self.pool.commit_status_pool[sha256].ki = n - self.pool.commit_status_pool[sha256].ki
        if self.init_status.left is not None and self.init_status.right is not None:
            self.sendto(msg, self.init_status.left.addr)
            self.sendto(msg, self.init_status.right.addr)
        else:
            di = int_from_hex(self.init_status.private_key)
            ssum = (di * challenge * self.pool.commit_status_pool[sha256].ai + self.pool.commit_status_pool[sha256].ki) % n
            rst_msg = {
                "type": ConsensusMsg.follower.RESPONSE,
                "sha256": sha256,
                "ssum": ssum,
            }
            self.sendto(rst_msg, addr)

    def aggregate_response_(self, sha256):
        di = int_from_hex(self.init_status.private_key)
        left_ssum = self.pool.left_response_pool[sha256]
        right_ssum = self.pool.right_response_pool[sha256]
        challenge = self.pool.challenge_pool[sha256]
        ai = self.pool.commit_status_pool[sha256].ai
        ki = self.pool.commit_status_pool[sha256].ki
        ssum =left_ssum+right_ssum+(di*challenge*ai+ki)%n
        return ssum

    @handle_msg.register(ConsensusMsg.follower.RESPONSE)
    @check_role(RoleType.LEADER, RoleType.FOLLOWER)
    def aggregate_response(self, type, msg, addr):
        sha256 = msg["sha256"]
        ssum = msg["ssum"]
        if tuple(addr)==self.init_status.left.addr:
            self.pool.left_response_pool[sha256] = ssum
        elif tuple(addr)==self.init_status.right.addr:
            self.pool.right_response_pool[sha256] = ssum
        else:
            logging.error("Parent node receive msg from wrong node!")
        
        if sha256 in self.pool.left_response_pool.keys() and sha256 in self.pool.right_response_pool.keys():
            ssum = self.aggregate_response_(sha256)
            if self.init_status.role == RoleType.FOLLOWER:
                rst_msg = {
                    "type": ConsensusMsg.follower.RESPONSE,
                    "sha256": sha256,
                    "ssum": ssum,
                }
                self.sendto(rst_msg, self.init_status.parent.addr)
            elif self.init_status.role == RoleType.LEADER:
                ssum = ssum%n
                sig = bytes_from_point(self.pool.commit_status_pool[sha256].rsum)+bytes_from_int(ssum)
                pub_key = bytes_from_point(self.pool.commit_status_pool[sha256].x)
                if schnorr_verify(bytes.fromhex(sha256), pub_key, sig):
                # 到这里流程走完了.
                    logging.warning("all path done.")
                else:
                    logging.warning("not pass!")
                self.sendto(msg, self.client_addr)
            else:
                raise RuntimeError("This line should not be exec!")

    # @handle_msg.register(ConsensusMsg.follower.RESET)
    # # 谁应该主动发起reset？follower吗？
    # # 主动发动reset的类型，与接收reset的命令类型应该一致吗？是否需要主动和被动两种处理？
    # # @check_role()
    # def reset_self(self, type, msg, addr):
    #     # reset 应该发送给谁?
    #     self.sendto(None, None)
    #     pass

    def is_valid(self, msgs):
        return True
