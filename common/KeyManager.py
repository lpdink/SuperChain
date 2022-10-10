"""
Author: lpdink
Date: 2022-10-07 11:01:31
LastEditors: lpdink
LastEditTime: 2022-10-10 09:06:30
Description: 
"""
import rsa
from cryptography.fernet import Fernet
from common import config


class KeyManager:
    @staticmethod
    def generate_pair():
        pub, priv = rsa.newkeys(config.key.pair_key_length)
        pub = {"pub-n": pub.n, "pub-e": pub.e}
        return pub, priv

    @staticmethod
    def generate_key():
        return Fernet.generate_key()

    @staticmethod
    def encrypt(text, key):
        fernet = Fernet(key)
        return fernet.encrypt(text)

    @staticmethod
    def encrypt_with_pub(msg, pub_key):
        pub_key = rsa.PublicKey(pub_key["pub-n"], pub_key["pub-e"])
        # 不好加密dict,否则无法复原
        crypto = rsa.encrypt(msg, pub_key)
        return crypto

    @staticmethod
    def decrypt(token, key):
        fernet = Fernet(key)
        msg = fernet.decrypt(token)
        return msg

    @staticmethod
    def decrypt_with_rsa(token, priv_key):
        msg = rsa.decrypt(token, priv_key).decode("utf-8")
        return msg
