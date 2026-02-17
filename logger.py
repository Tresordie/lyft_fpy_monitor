# !usr/bin/env python
# -*- coding:utf-8 -*-

"""
Description  :
Version      : 1.0
Author       : simon.yuan
Date         : 2024-01-13 16:40:09
LastEditors  : simon.yuan
LastEditTime : 2026-02-17 22:51:42
FilePath     : \\lyft_fpy_monitor\\logger.py
"""

import logging
from logging import handlers


class Logger(object):
    level_relations = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "crit": logging.CRITICAL,
    }

    def __init__(
        self,
        filename,
        level="info",
        when="D",
        backCount=3,
        fmt="%(asctime)s - %(pathname)s - %(levelname)s: %(message)s",
    ):
        # logger file name
        self.logger = logging.getLogger(filename)

        # logger level
        self.logger.setLevel(self.level_relations.get(level))

        # logger format
        format_str = logging.Formatter(fmt)

        # logger to console
        console_log = logging.StreamHandler()
        # logger to console's format
        console_log.setFormatter(format_str)

        file_log = handlers.TimedRotatingFileHandler(
            filename=filename, when=when, backupCount=backCount, encoding="utf-8"
        )  # 往文件里写入#指定间隔时间自动生成文件的处理器
        # 实例化TimedRotatingFileHandler
        # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时
        # D 天
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        file_log.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(console_log)  # 把对象加到logger里
        self.logger.addHandler(file_log)
