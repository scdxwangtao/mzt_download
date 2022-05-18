# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: test_forum_page.py
@CreateTime: 2022/5/13 16:08
"""
import asyncio

from core import forum_page


def test_get_forum_name_list():
    referer = "https://mmzztt.com/"
    forum_page_url = "https://mmzztt.com/photo/tag/"
    forum_name_list = asyncio.get_event_loop().run_until_complete(
        forum_page.get_forum_name_list(referer=referer,
                                       forum_page_url=forum_page_url))
    return forum_name_list


def test_get_forum_list():
    referer = "https://mmzztt.com/"
    forum_name = "尤物"
    forum_url = "https://mmzztt.com/photo/tag/youwu/"     # 多页
    # forum_url = "https://mmzztt.com/photo/tag/cosplay/"     # 一页
    forum_list = asyncio.get_event_loop().run_until_complete(forum_page.get_forum_page_list(
        referer=referer,
        forum_name=forum_name,
        forum_url=forum_url))
    return forum_list


if __name__ == '__main__':
    print(test_get_forum_name_list())
    print(test_get_forum_list())
