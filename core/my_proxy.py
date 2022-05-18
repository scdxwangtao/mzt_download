# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: my_proxy.py
@CreateTime: 2022/5/14 16:58
"""
import asyncio
import json
import random
import telnetlib

import requests
from pyppeteer import launch

from core import my_tools


async def main(save_path, set_proxy_type, proxy_url=None):
    # proxy_host = "127.0.0.1"
    # proxy_port = 10809
    # # proxy_host = "43.255.113.232"
    # # proxy_port = 82
    # proxy_host_port = proxy_host + ":" + str(proxy_url)
    browser = await launch({
        # "headless": False,
        'args': ['--proxy-server={}'.format(proxy_url),
                 '--start-maximized',
                 ],  # 设置代理不然不能获取
    })
    page = await browser.newPage()
    await my_tools.set_page(page)
    proxy_url_api = 'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list'
    result = await page.goto(proxy_url_api, {"timeout": 1 * 60000})
    proxies_list = parse(await result.text(), save_path, set_proxy_type)
    await browser.close()
    return proxies_list


def parse(response, save_path, set_proxy_type="json"):
    """main()方法回调函数
    :param set_proxy_type json or url
    :param response main function return
    """
    if response is not None:
        print("proxy from the web page succeeded!!!")
    # print(response.split('\n'))
    proxies_list = []
    for proxy in response.split('\n'):
        # print(proxy)
        if proxy != '':
            proxy_json = json.loads(proxy)
            proxy_host = proxy_json['host']
            proxy_port = proxy_json['port']
            proxy_type = proxy_json['type']
            proxies = verify(proxy_host, proxy_port, proxy_type, set_proxy_type, save_path)
            if proxies is not None:
                if set_proxy_type == "json":
                    proxies_list.append(proxies)

                elif set_proxy_type == "url":
                    proxy_host = proxy_json['host']
                    proxy_port = proxy_json['port']
                    proxy_type = proxy_json['type']
                    proxy_url = str(proxy_type) + "://" + str(proxy_host) + ":" + str(proxy_port)
                    proxies_list.append(proxy_url)
    return proxies_list


# 定义函数,验证代理ip是否有效
def verify(proxy_host, proxy_port, proxy_type, set_proxy_type, save_path):
    """定义函数,验证代理ip是否有效,返回有效代理"""
    proxies = {}
    proxy_url = str(proxy_type) + "://" + str(proxy_host) + ":" + str(proxy_port)
    try:
        telnet = telnetlib.Telnet(host=proxy_host, port=proxy_port, timeout=3)  # 用这个ip请访问，3s自动断开，返回tiemout
        proxies['type'] = proxy_type
        proxies['host'] = proxy_host
        proxies['port'] = proxy_port
        proxies_json = json.dumps(proxies)
        # 保存到本地的proxies_ip.json文件
        if set_proxy_type == "json":
            with open('{}/proxies_ip_json.json'.format(save_path), 'a+', encoding="utf-8") as f:
                f.write(proxies_json + '\n')
        elif set_proxy_type == "url":
            with open('{}/proxies_ip_url.txt'.format(save_path), 'a+', encoding="utf-8") as f:
                f.write(proxy_url + '\n')
        print("connected successfully!!!   代理链接为：{}   已写入：{}".format(proxy_url, proxies))
        telnet.close()
        return proxies
    except Exception as e:
        print('unconnected!!!  代理链接为：{}  exception as: {}'.format(proxy_url, e))
        return


def get_proxy_list_to_web(save_path, set_proxy_type, proxy_url):
    # main是异步执行的，需要用这行代码来执行，而不是直接main()
    loop = asyncio.get_event_loop()
    proxy_list = loop.run_until_complete(main(save_path, set_proxy_type, proxy_url=proxy_url))
    loop.close()
    return proxy_list


def get_proxy_list_to_localhost(proxies_ip_path, set_proxy_type="json"):
    """从本地json文件中获取配置文件"""
    proxy_list = []
    json_file = my_tools.read_file(proxies_ip_path, "r")
    for temp in json_file:
        temp = temp.rstrip("\n")
        proxy_json = json.loads(temp)
        if set_proxy_type == "json":
            proxy_list.append(proxy_json)
        elif set_proxy_type == "url":
            proxy_host = proxy_json['host']
            proxy_port = proxy_json['port']
            proxy_type = proxy_json['type']
            proxy_url = str(proxy_type) + "://" + str(proxy_host) + ":" + str(proxy_port)
            proxy_list.append(proxy_url)
    return proxy_list


def get_pdl_url_api(url, save_path, proxies_ip_url_path):
    url_api = "https://www.padaili.com/proxyapi?api=Fouj4wbArFW3op2qHBvZZh4SwfgiZSQI&num=100" \
              "&type=1&cunhuo=2&xiangying=1&order=xiangying"
    response = my_tools.get_url(url=url_api)
    response_text = response.text.replace("<br/>", "\n")
    print(response_text)
    with open('{}/proxies_ip_url.txt'.format(save_path), 'a+', encoding="utf-8") as f:
        f.write(response_text)
    return response_text


def chick_ip_json(url, save_path, proxies_ip_path: object) -> object:
    save_filename = save_path + '/can_use_ip_url.txt'
    my_tools.remove_file(save_filename)  # 删除现有可使用代理文件
    proxies_list = get_proxy_list_to_localhost(proxies_ip_path, "url")
    ip_list = []
    proxies = None
    for proxies_ in proxies_list:
        if proxies_.split(":")[0] == "http":
            proxies = {'http': proxies_.rstrip("\n")}
        elif proxies_.split(":")[0] == "https":
            proxies = {'https': proxies_.rstrip("\n")}
        elif proxies_.split(":")[0] == "socks5":
            proxies = {'socks5': proxies_.rstrip("\n")}
        try:
            wb_data = requests.get(url=url, proxies=proxies)
            print(wb_data.status_code)
            flag = True
            print("\033[1;0;32m 当前检查IP可用，IP地址为：{}\033[0m".format(proxies_))
        except:
            proxies_list.remove(proxies_)
            flag = False
            print("\033[1;0;31m 当前检查IP不可用，IP地址为：{}\033[0m".format(proxies_))
        if flag:
            ip_list.append(proxies_)
            with open(save_filename, 'a+', encoding="utf-8") as f:
                f.write(proxies_ + '\n')
    return ip_list


def chick_ip_urls(url, save_path, proxies_ip_url_path):
    save_filename = save_path + '/can_use_ip_url.txt'
    my_tools.remove_file(save_filename)     # 删除现有可使用代理文件
    proxies_list = my_tools.read_file(proxies_ip_url_path, "r")
    ip_list = []
    proxies = None
    for proxies_ in proxies_list:
        if proxies_.split(":")[0] == "http":
            proxies = {'http': proxies_.rstrip("\n")}
        elif proxies_.split(":")[0] == "https":
            proxies = {'https': proxies_.rstrip("\n")}
        elif proxies_.split(":")[0] == "socks5":
            proxies = {'socks5': proxies_.rstrip("\n")}
        try:
            wb_data = requests.get(url=url, proxies=proxies)
            print(wb_data.status_code)
            flag = True
            print("\033[1;0;32m 当前检查IP可用，IP地址为：{}\033[0m".format(proxies_))
        except Exception as e:
            print(e)
            proxies_list.remove(proxies_)
            flag = False
            print("\033[1;0;31m 当前检查IP不可用，IP地址为：{}\033[0m".format(proxies_))
        if flag:
            ip_list.append(proxies_)
            with open(save_filename, 'a+', encoding="utf-8") as f:
                f.write(proxies_)
    return ip_list


def get_proxy_ip(path):

    proxies_list = my_tools.read_file(path, "r")
    # use_ip  format: --> HOST:PORT
    use_ip = random.choice(proxies_list)
    use_ip = use_ip.lstrip("http://").lstrip("https://")
    # print("ip池总可用数量为：{}".format(len(proxies_list)))
    print("\033[1;0;32m 当前页面使用代理ip为：{}\033[0m".format(use_ip))
    return use_ip


def chick_page_ip(proxies):
    """http://pv.sohu.com/cityjson 查看当前ip是否切换，获取这个链接的数据即可"""
    url = "http://pv.sohu.com/cityjson"
    response = my_tools.get_url(url=url, proxies=proxies)
    if response is not None:
        response = response.text.lstrip("var returnCitySN = ").rstrip(";")
        # response1 = my_tools.get_url(url="https://www.mmzztt.com", proxies=proxies)
        proxy_json = json.loads(response)
        proxy_host = proxy_json['cip']
        proxy_cname = proxy_json['cname']
        proxy_address = "\033[1;0;32m 当前使用代理ip为：{}, 当前ip城市为：{}\033[0m".format(proxy_host, proxy_cname)
        print(proxy_address)
        return proxy_address
