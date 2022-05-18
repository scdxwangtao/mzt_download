# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: test_logger.py
@CreateTime: 2022/5/15 12:30
"""
from logs.logger import MyLogger

if __name__ == '__main__':
    # log = Logger('log/all.log', level='debug')
    # log.logger.debug(set_str_color("debug", "white"))
    # log.logger.info(set_str_color("info", "green"))
    # log.logger.warning(set_str_color("警告", "yellow"))
    # log.logger.error(set_str_color("报错", "red"))
    # log.logger.critical(set_str_color("严重", "pink"))
    logger = MyLogger()
    logger.warning("test")
    # try:critical
    #     print(5555555555)
    #     print(5 / 0)
    # except Exception as e:
    #     log.logger.error("\n" + str(traceback.format_exc()))
    # Logger('error.log', level='error').logger.error('error')