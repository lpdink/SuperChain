"""
Author: lpdink
Date: 2022-10-13 07:23:52
LastEditors: lpdink
LastEditTime: 2022-10-13 07:25:05
Description: 
"""
import hashlib


def sha256(text: str):
    text = text.encode("utf-8")
    return hashlib.sha256(text).hexdigest()
