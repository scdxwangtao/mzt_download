# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: test_my_proxy.py
@CreateTime: 2022/5/14 16:59
"""
from core.my_proxy import get_proxy_list_to_web, chick_ip_urls, chick_ip_json, get_proxy_ip, get_pdl_url_api, chick_page_ip

# import urllib3.contrib.pyopenssl
# urllib3.contrib.pyopenssl.inject_into_urllib3()

url = 'https://www.mmzztt.com/'
# url = 'https://www.baidu.com/'
# print(get_proxy_list_to_web("../conf", "url", proxy_url="127.0.0.1:10809"))
# print(get_proxy_list_to_web("../conf", "json", proxy_url="127.0.0.1:10809"))    # 已自检查一次
# print(get_proxy_list_to_localhost("../conf/proxies_ip.json"))
# chick_ip_json(url, "../conf", "../conf/proxies_ip_json.json")
# get_pdl_url_api(url, "../conf", "../conf/proxies_ip_url.txt")
chick_ip_urls(url, "../conf", "../conf/proxies_ip_url.txt")

# use_ip = get_proxy_ip(path="../conf/can_use_ip_url.txt")
# use_ip = "127.0.0.1:10809"
# chick_page_ip(proxies=use_ip)