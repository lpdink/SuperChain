"""
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-10 08:35:51
Description: 支持工厂模式。
"""
from common import logging
import sys


class Factory:
    def __init__(self) -> None:
        self.name2clazz = dict()
        self.clazz2name = dict()
        self.name2obj = dict()
        self.obj2name = dict()

    def __call__(self, name):
        def register(clazz):
            if name not in self.name2clazz:
                self.name2clazz[name] = clazz
            else:
                logging.error(f"class name {name} already registered!")
                sys.exit(-1)
            if clazz not in self.clazz2name:
                self.clazz2name[clazz] = name
            else:
                logging.error(
                    f"class already registered with name {self.clazz2name[clazz]}!"
                )
                sys.exit(-1)
            return clazz

        return register

    def get(self, obj_name):
        return self[obj_name]

    def __getitem__(self, key):
        return self.name2obj.get(key, None)

    def create_obj_from_config(self, config):
        if hasattr(config, "objects"):
            for obj in config.objects:
                clazz = self.name2clazz.get(obj.clazz, None)
                if clazz is None:
                    logging.warning(f"no clazz in {obj}, so it is not instanced")
                    continue
                # 如果配置了，使用配置的
                if len(obj.args) > 0:
                    new_obj = clazz(**obj.args)
                # 否则使用默认参数
                else:
                    new_obj = clazz()
                self.name2obj[obj.name] = new_obj
                self.obj2name[new_obj] = obj.name
                logging.info(f"created instance with {obj}")
        if hasattr(config, "objects_group"):
            for group in config.objects_group:
                clazz = self.name2clazz.get(group.clazz, None)
                if clazz is None:
                    logging.warning(f"no clazz in {group}, so they are not instanced")
                    continue
                if len(group.args) > 0:
                    obj_pool = [clazz(**group.args) for _ in range(group.nums)]
                else:
                    obj_pool = [clazz() for _ in range(group.nums)]
                self.name2obj[group.name] = obj_pool
                logging.info(f"created instance with {group}")


factory = Factory()

if __name__ == "__main__":
    """
    根据config.json创建对象
    """
    pass
