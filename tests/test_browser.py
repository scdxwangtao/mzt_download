# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: test_browser.py
@CreateTime: 2022/5/7 19:28
"""
import asyncio

import pyppeteer

from core import my_browser
from logs.logger import MyLogger


async def test_get_page():
    print('默认版本是：{}'.format(pyppeteer.__chromium_revision__))
    print('可执行文件默认路径：{}'.format(pyppeteer.chromium_downloader.chromiumExecutable.get('win64')))
    print('win64平台下载链接为：{}'.format(pyppeteer.chromium_downloader.downloadURLs.get('win64')))

    logger = MyLogger()
    url = "https://mmzztt.com/photo/65429"
    referer = "https://mmzztt.com/"
    driver = await my_browser.get_browser(logger=logger)
    page_response = await my_browser.get_page(browser=driver, url=url, referer=referer)
    page = page_response[0]
    res = page_response[1]
    resp_headers = res.headers  # 响应头
    resp_status = res.status  # 响应状态
    print(resp_headers)
    print(resp_status)
    # print(await page.content())
    # print(await res.text())
    # 获取第一页的数据
    page_text = await page.content()  # 获取页面内容
    # print(page_text)
    await page.close()
    await driver.close()


if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(test_get_page())


