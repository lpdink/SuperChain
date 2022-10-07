'''
Author: lpdink
Date: 2022-10-07 01:59:10
LastEditors: lpdink
LastEditTime: 2022-10-07 03:33:38
Description: 
'''
import logging
import os
from datetime import datetime
LOG_DIR = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "../resources/log")
COLOR_DIC = {
    'ERROR': "31",
    'INFO': "37",
    'DEBUG': "34",
    'WARN': "33",
    'WARNING': "33",
    'CRITICAL': "35",
}


class ColorFormatter(logging.Formatter):
    def __init__(self, fmt, use_color=False) -> None:
        super().__init__(fmt)
        self.use_color = use_color

    def format(self, record) -> str:
        color = COLOR_DIC[record.levelname]
        return f"\033[{color}m{super().format(record)}\033[0m" if self.use_color else super().format(record)


class Logger(logging.Logger):
    def __init__(self, name="log", level=0) -> None:
        super().__init__(name, level)
        stream_handler = logging.StreamHandler()
        fmt = "[%(asctime)s %(levelname)s %(pathname)s at line %(lineno)d] %(message)s"
        color_formater = ColorFormatter(fmt, True)
        stream_handler.setFormatter(color_formater)
        if not os.path.isdir(LOG_DIR):
            os.makedirs(LOG_DIR)
        now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        log_file_path = os.path.join(LOG_DIR, f"{now}.txt")
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_format = logging.Formatter(fmt)
        file_handler.setFormatter(file_format)
        self.addHandler(stream_handler)
        self.addHandler(file_handler)


logging = Logger()
if __name__ == "__main__":
    logging.debug("I am debug")
    logging.info("I am info")
    logging.warning("I am warn")
    logging.error("I am error")
