# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: test_beauty_exists_download.py
@CreateTime: 2022/5/18 10:21
"""
import asyncio
import os
import shutil
import threading
from pathlib import Path

import aiohttp

from core import my_browser, my_tools
from core.detail_page import beauty_exists_download
from logs.logger import MyLogger


async def test_beauty_exists_download():
    logger = MyLogger()  # 自定义日志
    lock = threading.RLock()  # 初始化线程锁
    browser = await my_browser.get_browser(logger)
    referer = "https://mmzztt.com/"
    txt_path = "../datas/tmp_txt/"
    dir_path = '../datas/images/beauty/'
    forum_name = "自拍"
    sleep_times = 1.0
    # 多种类型测试
    # page_url = "https://mmzztt.com/beauty/66993"    # 4页
    # page_name = "她又骗我电脑坏了"
    # page_number = "66993"
    # create_time = "2022-05-14"

    # page_url = "https://mmzztt.com/beauty/728"    # 2页
    # page_name = "乃万美爆了"
    # page_number = "728"
    # create_time = "2020-10-07"

    page_url = "https://mmzztt.com/beauty/959"    # 1页
    page_name = "阚清子到底有多惊艳"
    page_number = "959"
    create_time = "2020-10-08"

    timeout = aiohttp.ClientTimeout(total=3600 * 24, connect=60, sock_connect=60, sock_read=60)
    semaphore = asyncio.Semaphore(16)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=32, ssl=False),  # 不使用代理
                                     timeout=timeout,
                                     headers=my_tools.get_headers(referer)) as session:
        if os.path.exists("../datas/images/beauty/{}_{}_{}_{}".format(forum_name, create_time, page_number, page_name)):
            shutil.rmtree("../datas/images/beauty/{}_{}_{}_{}".format(forum_name, create_time, page_number, page_name))
        if os.path.exists("../datas/tmp_txt/beauty_img_urls.txt"):
            os.remove("../datas/tmp_txt/beauty_img_urls.txt")
        await beauty_exists_download(browser, referer, session, semaphore, dir_path, txt_path, logger, lock, forum_name,
                                     page_name, page_number, create_time, page_url, sleep_times=sleep_times)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_beauty_exists_download())  # 潮拍馆启动程序
