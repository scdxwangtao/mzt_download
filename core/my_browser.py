# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: my_browser.py
@CreateTime: 2022/5/7 19:22
"""
import asyncio
import os
import random
import shutil

import pyppeteer
from pyppeteer import launch

from core import my_tools

# 全局代理设置
proxy_url = "https://127.0.0.1:10809"


# proxy_url = my_proxy.get_proxy_ip("conf/can_use_ip_url.txt")


async def get_browser(logger):
    # 程序运行自动下载chromium报错或者下载很慢，可以设置环境变量使用淘宝加速镜像，
    # 或者在launch中设置参数executablePath指定已安装的chrome或者chromium路径
    os.environ["PYPPETEER_DOWNLOAD_HOST"] = "https://npm.taobao.org/mirrors"
    # 每次启动浏览器之前先清理一次缓存文件
    p = os.path.join(pyppeteer.__pyppeteer_home__, ".dev_profile")
    logger.info("pyppeteer使用的缓存地址为：{}，清除缓存文件".format(p))
    shutil.rmtree(p, ignore_errors=True)

    global proxy_url  # 声明代理未全局变量，方便修改

    logger.warning("当前正在使用代理为：{}".format(proxy_url))
    """浏览器 启动参数"""
    browser = await launch(
        # 启动chrome的路径，指定chromium软件的位置,可选本地已有浏览器
        # "executablePath": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        # 关闭无头浏览器 默认是无头启动的， 默认值为True
        # headless=True,
        # headless=False,
        # 是否忽略 Https 报错信息，默认为 False
        ignoreHTTPSErrors=True,
        # 去除Chrome正受到自动测试软件的控制提示, 无法关闭(Chrome 正受到自动测试软件的控制)这个控制条,新版使用有副作用。
        # 启动后关闭需要关闭args中 '--disable-infobars',
        # ignoreDefaultArgs=['--enable-automation'],
        # 用户数据目录的路径。
        userDataDir="datas",
        # 防止页面多开阻塞
        dumpio=True,
        # 设置浏览器对象自动关闭
        autoClose=True,
        # 设置打印日志级别
        logLevel='ERROR',
        # 其他参数
        args=[
            # 不显示信息栏，比如：chrome正在受到自动测试软件的控制，无法关闭(Chrome 正受到自动测试软件的控制)这个控制条，旧版使用。
            '--disable-infobars',
            # 最大化显示
            '--start-maximized',
            # 取消沙盒模式，放开权限，无头浏览器模式必须打开这个，不然报错。
            "--no-sandbox",
            # 如果要单独写到配置高宽，需要在window-size前面加上f
            # f'--window-size={width},{height}',
            # 设置代理
            f'--proxy-server={proxy_url}'
            # '--proxy-server={}'.format(proxy_url),
            ''' 
                '--proxy-server=socks5://111.111.123.111,  socks5
                '--proxy-server=http://111.111.123.111,    http
                '--proxy-server=https://111.111.123.111,   https
            '''
            # '--proxy-server=' + my_proxy.get_proxy_ip("conf/can_use_ip_url.txt"),
        ],
    )
    return browser


async def get_page(browser, url, referer=None):
    # browser = await get_browser()
    headers = my_tools.get_headers(referer)
    # 创建一个页面对象， 页面操作在该对象上执行
    # page = await browser.newPage()
    pages = await browser.pages()
    page = pages[0]
    timeout = 300 * 1000       # 超时时间，毫秒

    # 设置页面宽高
    await my_tools.set_page(page)
    # 禁止加载JavaScript，可提高加载速度，视情况确定True/False，
    # await page.setJavaScriptEnabled(enabled=False)
    await page.setJavaScriptEnabled(enabled=True)  # 此网页必须启用，不然模拟点击不能生效
    # 开启缓存，开启缓存才能下载完全。关闭要报错。
    await page.setCacheEnabled(True)
    # 运行js来修改window.navigator.webdriver属性值，绕过webdriver检测
    # # 旧版
    # await page.evaluateOnNewDocument('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
    # 新版
    await page.evaluateOnNewDocument(
        'function(){Object.defineProperty(navigator, "webdriver", {get: () => undefined})}')
    # 设置headers
    await page.setExtraHTTPHeaders(headers)
    # timeout修改默认时间，否则报错 Navigation Timeout Exceeded: 30000 ms exceeded.
    page.setDefaultNavigationTimeout(timeout=timeout)
    response = None
    try:
        # response = await page.goto(url=url, options={"waitUntil": 'domcontentloaded', "timeout": 60 * 1000})  # 页面跳转
        # response = await page.goto(url=url, options={"waitUntil": 'domcontentloaded', })  # 页面跳转
        # response = await page.goto(url=url, options={"waitUntil": 'load'})
        # 网站超时不报错，进程假死时使用这
        response = await asyncio.wait_for(page.goto(url, {'waitUntil': ['load', 'networkidle0'], "timeout": timeout}),
                                          timeout / 1000 + 1)
        # response = await page.goto(url=url, options={"waitUntil": 'networkidle0'})
        # response = await page.goto(url=url, options={"waitUntil": 'networkidle2'})
        # response = await page.goto(url=url)
    except TimeoutError as e:
        print(e)
        # page.goto超时之后偶尔失去响应
        await page._client.send("Page.stopLoading")
    await asyncio.sleep(random.uniform(0.8, 1.2))
    return page, response
