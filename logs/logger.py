# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: logger.py
@CreateTime: 2022/5/15 10:32
"""
import logging
import time
import traceback
from logging import handlers
from pathlib import Path

from core.my_tools import set_str_color, my_print


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(self, filename, level='info', when='D', backCount=3,
                 fmt=set_str_color('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s', "cyan")):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                               encoding='utf-8')  # 往文件里写入#指定间隔时间自动生成文件的处理器
        # 实例化TimedRotatingFileHandler
        # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)


class MyLogger:
    def __init__(self, log_path="../logs/log/", level='debug', file_name=None):
        self.log_path = log_path
        if file_name is None:
            self.file_name = 'log_' + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + '.log'
        else:
            self.file_name = file_name
        self.log_file_path = self.log_path + self.file_name
        my_print(self.log_file_path, "yellow")
        self.log = Logger(str(self.log_file_path), level=level)

    def debug(self, msg):
        self.log.logger.debug(set_str_color(msg, "white"))

    def info(self, msg):
        self.log.logger.debug(set_str_color(msg, "green"))

    def warning(self, msg):
        self.log.logger.debug(set_str_color(msg, "yellow"))

    def error(self, msg):
        self.log.logger.debug(set_str_color(msg, "red"))

    def critical(self, msg):
        self.log.logger.debug(set_str_color(msg, "pink"))
