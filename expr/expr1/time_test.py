from config import config
import time
import os
import matplotlib.pyplot as plt

def test_ecdsa():
    from ecdsa import SigningKey, SECP256k1
    rst = []
    sk = SigningKey.generate(SECP256k1)
    msg = os.urandom(config.msg_length)
    sign = sk.sign(msg)

    for node_nums in config.node_nums:
        start = time.perf_counter()
        for _ in range(config.run_times):
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
    for node_nums in config.node_nums:
        start = time.perf_counter()
        for _ in range(config.run_times):
            result = sl.schnorr_verify(M, pubkey_bytes, sig_bytes)
        end = time.perf_counter()
        rst.append(end-start)
    return rst

def draw():
    