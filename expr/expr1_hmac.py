import os
from timer import timer
from cryptography.hazmat.primitives import hashes, hmac

def generate_sign(node_nums):
    # 比特币的私钥长度一般为32.
    key = os.urandom(32)
    h = hmac.HMAC(key, hashes.SHA256())
    for _ in range(node_nums):
        # 一条交易长度取250
        msg = os.urandom(250)
        h.update(msg)
    signature = h.finalize()
    return h, signature

@timer
def verify(sign, run_nums):
    for _ in range(run_nums):
        h.verify(sign)

if __name__=="__main__":
    for node_num in range(1, 32):
        h, sign = generate_sign(node_num)
        verify(h, sign, 1)
        print(f"node_num:{node_num}")