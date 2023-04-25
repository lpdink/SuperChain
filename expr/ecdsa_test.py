import os
import time
import matplotlib.pyplot as plt
from tqdm import tqdm
# 导入cryptography库中的相关模块
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature

def generate_sign():
    # 生成一对ECDSA密钥，使用secp256r1曲线
    private_key = ec.generate_private_key(ec.SECP256K1())
    public_key = private_key.public_key()

    # 待签名的消息, 取250长度
    message = os.urandom(250)

    # 使用私钥对消息进行签名，使用SHA256作为哈希函数
    signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
    # breakpoint()
    public_key.verify
    return signature, public_key, message

def verify(pub_key, sign, message, run_times, node_nums):
    start = time.perf_counter()
    # 使用公钥对签名进行验证，使用SHA256作为哈希函数
    for _ in range(run_times):
        for _ in range(node_nums-1):
            pub_key.verify(sign, message, ec.ECDSA(hashes.SHA256()))
    end = time.perf_counter()
    print(f"node {node_nums} run {run_times} use {end-start} s")
    return end-start

def main():
    sign, pub_key, msg = generate_sign()
    verify(pub_key, sign, msg, 100000, 1)
    node_nums = [2**i for i in range(2, 11)]
    # node_nums = list(range(4, 100))
    time_used = []
    for node_num in tqdm(node_nums):
        time_used.append(verify(pub_key, sign, msg, 10, node_num))
    plt.plot(node_nums, time_used, color="blue", label="run 10 times")
    # plt.bar(range(len(node_nums)), time_used, color="blue", label="run 10 times")
    plt.xticks(range(len(node_nums)), node_nums)

    plt.xlabel("node nums")
    plt.ylabel("time used(s)")
    plt.savefig("linear.png")
    

if __name__=="__main__":
    main()