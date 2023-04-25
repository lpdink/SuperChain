from config import config
from tqdm import tqdm
import time
import os
import matplotlib.pyplot as plt
import sys
sys.path.append("./schnoor_repo")

def test_ecdsa():
    from ecdsa import SigningKey, SECP256k1
    rst = []
    sk = SigningKey.generate(SECP256k1)
    msg = os.urandom(config.msg_length)
    sign = sk.sign(msg)
    print("test ecdsa...")
    for node_nums in tqdm(config.node_nums):
        start = time.perf_counter()
        for _ in tqdm(range(config.run_times), leave=False, desc=f"node_nums:{node_nums}"):
            for _ in range(node_nums):
                sk.verifying_key.verify(sign, msg)
        end = time.perf_counter()
        rst.append(end-start)
    return rst

def test_schnoor():
    import schnoor_repo.create_keypair as ckp
    import schnoor_repo.schnorr_lib as sl
    rst = []
    user = ckp.create_keypair(1)["users"]

    M = os.urandom(config.msg_length)
    M = sl.sha256(M)

    sig = sl.schnorr_sign(M, user[0]["privateKey"])

    pubkey_bytes = bytes.fromhex(user[0]["publicKey"])
    # print("Signature =",sig.hex())

    sig_bytes = sig
    print("test schnorr")
    for node_nums in tqdm(config.node_nums):
        start = time.perf_counter()
        for _ in tqdm(range(config.run_times), leave=False, desc=f"node_nums:{node_nums}"):
            result = sl.schnorr_verify(M, pubkey_bytes, sig_bytes)
        end = time.perf_counter()
        rst.append(end-start)
    return rst

def test_bls():
    from py_ecc.bls import G2ProofOfPossession as bls_pop

    private_key = 5566
    public_key = bls_pop.SkToPk(private_key)

    message = os.urandom(config.msg_length)

    # Signing
    signature = bls_pop.Sign(private_key, message)

    # Verifying
    rst = []
    print("test bls")
    for node_nums in tqdm(config.node_nums):
        start = time.perf_counter()
        for _ in tqdm(range(config.run_times), leave=False, desc=f"node_nums:{node_nums}"):
            bls_pop.Verify(public_key, message, signature)
        end = time.perf_counter()
        rst.append(end-start)
    return rst

def test_rsa():
    import rsa

    (pubkey, privkey) = rsa.newkeys(config.msg_length*9)
    message = os.urandom(config.msg_length)
    signature = rsa.sign(message, privkey, 'SHA-256')

    print("test rsa...")
    rst = []
    for node_nums in tqdm(config.node_nums):
        start = time.perf_counter()
        for _ in tqdm(range(config.run_times), leave=False, desc=f"node_nums:{node_nums}"):
            for _ in range(node_nums):
                rsa.verify(message, signature, pubkey)
        end = time.perf_counter()
        rst.append(end-start)
    return rst


def draw():
    if config.run_schnoor:
        schnoor_rst = test_schnoor()
        plt.plot(range(len(config.node_nums)), schnoor_rst, label="schnoor")
    if config.run_ecdsa:
        ecdsa_rst = test_ecdsa()
        plt.plot(range(len(config.node_nums)), ecdsa_rst, label="ecdsa")
    if config.run_bls:
        bls_rst = test_bls()
        plt.plot(range(len(config.node_nums)), bls_rst, label="bls")
    if config.run_rsa:
        rsa_rst = test_rsa()
        plt.plot(range(len(config.node_nums)), rsa_rst, label="rsa")
    plt.xticks(range(len(config.node_nums)), config.node_nums)
    plt.xlabel("node nums")
    plt.ylabel(f"run {config.run_times} times used(s)")
    plt.legend()
    plt.savefig(f"{__file__}.png")

if __name__=="__main__":
    draw()