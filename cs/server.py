"""
Author: lpdink
Date: 2022-10-07 02:34:16
LastEditors: lpdink
LastEditTime: 2022-10-07 07:34:44
Description: 后端业务主服务器，用于批量创建及管理节点，监测节点性能。
"""
from common import logging
from framework import factory
from multiprocessing import Process
import random


class Server:
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self, config) -> None:
        factory.create_obj_from_config(config)
        self._service_group = factory["service_group"]
        self._super_group = factory["super_group"]
        self._cross_group = factory["cross_group"]
        self._process_pool = []

    @property
    def service(self):
        return random.choice(self._service_group)

    @property
    def super(self):
        return random.choice(self._super_group)

    @property
    def cross(self):
        return random.choice(self._cross_group)

    def run(self, behind=False):
        for service in self._service_group:
            service_process = Process(target=service.run, daemon=behind)
            self._process_pool.append(service_process)
        for super in self._super_group:
            super_process = Process(target=super.run, daemon=behind)
            self._process_pool.append(super_process)
        for cross in self._cross_group:
            cross_process = Process(target=cross.run, daemon=behind)
            self._process_pool.append(cross_process)

        for process in self._process_pool:
            process.start()
        logging.info("Server begin running.")

    def shut_down(self):
        for process in self._process_pool:
            process.terminate()
        logging.info("Server shutdown.")
