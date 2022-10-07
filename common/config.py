"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-07 10:50:04
Description: 
"""
import json
import os

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../resources/config.json"
)


class Config:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if type(v) == dict:
                v = Config(**v)
            if type(v) == list:
                for index, item in enumerate(v):
                    if type(item) == dict:
                        v[index] = Config(**item)
            self[k] = v

    def get(self, key, default=None):
        if key in self.__dict__.keys():
            return getattr(self, key)
        else:
            return default

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()

    def values(self):
        return self.__dict__.values()

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, key):
        print(key)
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        return self.__dict__.__repr__()


def get_config(config_path):
    with open(config_path, "r") as file:
        content = file.read()
    data = json.loads(content)
    return Config(**data)


config = get_config(CONFIG_PATH)


if __name__ == "__main__":
    print(config)
    # for item in config:
    #     print(item)
    breakpoint()
