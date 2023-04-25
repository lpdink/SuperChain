from config import config
from tqdm import tqdm
import time
import os
import matplotlib.pyplot as plt
import sys
sys.path.append("./schnoor_repo")

def test_ecdsa():
    # 固定size: 64
    from ecdsa import SigningKey, SECP256k1
    sk = SigningKey.generate(SECP256k1)
    msg = os.urandom(config.msg_length)
    sign = sk.sign(msg)
    # print("test ecdsa...")
    breakpoint()

def test_schnoor():
    # 固定size:64
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
    print(len(sig))
    

def test_bls():
    # 固定size: 96
    from py_ecc.bls import G2ProofOfPossession as bls_pop

    private_key = 5566
    public_key = bls_pop.SkToPk(private_key)

    message = os.urandom(config.msg_length)

    # Signing
    signature = bls_pop.Sign(private_key, message)
    print(len(signature))

def test_rsa():
    # 取决于密钥长度/消息体长度，比较长，约282
    import rsa
    (pubkey, privkey) = rsa.newkeys(config.msg_length*9)
    message = os.urandom(config.msg_length)
    signature = rsa.sign(message, privkey, 'SHA-256')
    print(len(signature))

if __name__=="__main__":
    # test_ecdsa()
    # test_schnoor()
    # test_bls()
    test_rsa()
    pass