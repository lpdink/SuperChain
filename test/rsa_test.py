"""
Author: lpdink
Date: 2022-10-07 08:07:49
LastEditors: lpdink
LastEditTime: 2022-10-10 09:08:12
Description: 用于测试对称与非对称加密方案
"""
import rsa
from cryptography.fernet import Fernet


def generate_pair_key():
    (pubkey, privkey) = rsa.newkeys(512)
    return pubkey, privkey


def generate_single_key():
    key = Fernet.generate_key()
    return key


if __name__ == "__main__":
    with open("./resources/text.txt", "r", encoding="utf-8") as file:
        text = file.read().encode("utf-8")
    pub, pri = generate_pair_key()
    # 无法对过长文本加密，次行会OverflowError
    # crypto = rsa.encrypt(text, pub)
    # msg = rsa.decrypt(crypto, pri).decode("utf-8")
    # breakpoint()
    # 因此，先对文本进行对称加密。
    key = generate_single_key()
    f = Fernet(key)
    token = f.encrypt(text)
    msg = f.decrypt(token)
    print(f"msg==text? {msg==text}")
    # 再用非对称加密加密对称密钥。
    # breakpoint()
    crypto = rsa.encrypt(key, pub)
    msg_key = rsa.decrypt(crypto, pri)
    print(f"msg_key==key? {msg_key==key}")
    breakpoint()
