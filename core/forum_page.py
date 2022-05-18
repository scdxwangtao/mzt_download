# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: forum_page.py
@CreateTime: 2022/5/12 21:53
"""
from pathlib import Path

import aiohttp
from lxml import etree

from core import my_tools
from core.my_tools import aiohttp_get


async def get_forum_name_list(session, forum_page_url, logger):
    """通过https://mmzztt.com/photo/tag/链接，获取当前所有小板块名称和链接。"""
    forum_name_list = []
    # 获取页面内容，状态
    page_text, status = await aiohttp_get(session, forum_page_url)
    # print(f"html:{html}....")
    # print(f"status:{status}")
    logger.info(f"status:{status}")
    if status == 200:
        tree = etree.HTML(page_text)
        forum_lists = tree.xpath(
            "//ul[@class='uk-grid uk-grid-match uk-child-width-1-2@s g-list g-list-tag']/li/div/div/a")
        # print(len(forum_lists))
        for forum in forum_lists:
            forum_name = forum.xpath("img/@alt")[0]
            forum_name = my_tools.update_name(forum_name)
            forum_url = forum.xpath("@href")[0]
            forum_name_list.append((forum_name, forum_url))
    return forum_name_list


async def get_forum_page_list(session, forum_name, forum_url, semaphore, look, path, logger):
    """通过小板块名称，获取对应板块总页数和对应链接"""
    forum_name = my_tools.update_name(forum_name)
    forum_list = []
    fp = Path(path)

    # 加锁  使用线程锁，保证数据安全
    look.acquire()
    try:
        # 限制并发数量
        async with semaphore:
            # 获取页面内容和状态
            page_text, status = await aiohttp_get(session, forum_url)
            # print(page_text)
            if status == 200:
                tree = etree.HTML(page_text)
                page_count = tree.xpath(
                    "(//ul[@class='uk-pagination uk-flex-center uk-margin-remove uk-visible@s'])[1]/li/a/text()")
                if len(page_count) == 0:  # 没有总页数，表示只有一页数据
                    print("{}  |  总页数： {}。".format(forum_name, 1))
                    url = forum_url + "page/{}".format(str(1))
                    forum_list.append((forum_name, url))
                    # with open(fp.joinpath("{}.txt".format(forum_name)), "a+", encoding="utf-8") as f:
                    #     f.write(forum_name + "|" + url + "\n")
                    with open(fp.joinpath("tag_page.txt"), "a+", encoding="utf-8") as f:
                        f.write(forum_name + "|" + url + "\n")
                else:
                    print("{}  |  总页数： {}。".format(forum_name, page_count[-1]))
                    for i in range(int(page_count[-1])):
                        url = forum_url + "page/{}".format(str(i + 1))
                        forum_list.append((forum_name, url))
                        # with open(fp.joinpath("{}.txt".format(forum_name)), "a+", encoding="utf-8") as f:
                        #     f.write(forum_name + "|" + url + "\n")
                        with open(fp.joinpath("tag_page.txt"), "a+", encoding="utf-8") as f:
                            f.write(forum_name + "|" + url + "\n")
    finally:
        # 修改完成，释放锁
        look.release()
        return forum_list


async def get_detail_page_list(session, forum_name, forum_page_detail_url, semaphore, look, path, logger):
    """根据每一页链接，获取对应页面所有的图片链接标题等详细信息"""
    page_detail_list = []
    fp = Path(path)

    try:
        # 加锁  使用线程锁，保证数据安全
        look.acquire()
        # 限制并发数量
        async with semaphore:
            # 获取页面内容和状态
            page_text, status = await aiohttp_get(session, forum_page_detail_url)
            # print(page_text)
            tree = etree.HTML(page_text)
            forum_page_detail_list = tree.xpath(
                "(//ul[@class='uk-grid uk-grid-match uk-child-width-1-2@s uk-child-width-1-3@m g-list'])[1]/li/div")
            for page_detail in forum_page_detail_list:
                page_count = page_detail.xpath('div/text()')[0].rstrip("P")
                cover_rul = page_detail.xpath('div/a/img/@data-srcset')[0]
                page_name = page_detail.xpath('div/h2/a/text()')[0]
                page_name = my_tools.update_name(page_name)  # 修改不合规符号
                page_url = page_detail.xpath('div/h2/a/@href')[0]
                page_time = page_detail.xpath('div/time/text()')[0]
                page_time = page_time.split(" ")[0]     # 只取到天数，具体时分秒不要
                tup = forum_name, page_name, page_time, page_url.split("/")[-1], page_count, page_url, cover_rul
                logger.info(tup)
                # 保存信息
                with open(fp.joinpath("tag_name.txt"), "a+", encoding="utf-8") as f:
                    f.write(
                        forum_name + "|"                    # 板块名称
                        + page_name + "|"                   # 图片名称
                        + page_time + "|"                   # 图片时间
                        + page_url.split("/")[-1] + "|"     # 图片编号
                        + page_count + "|"                  # 图片张数
                        + cover_rul + "|"                   # 封面地址
                        + page_url + "|" + "\n"             # 图片地址
                    )
                page_detail_list.append(tup)
            #     # print(page_count)
            #     # print(page_name)
            #     # print(page_url)
            # # print(page_detail_list)
    finally:
        # 修改完成，释放锁
        look.release()
        return page_detail_list


async def get_beauty_page_count_url_list(session, beauty_url, logger):
    """
    通过程序进入页面，获取beauty所有页面地址。https://mmzztt.com/beauty/page/{}/
    :param session: aiohttp session
    :param beauty_url: https://mmzztt.com/beauty
    :param logger: logger日志
    :return:
    """
    # https://mmzztt.com/beauty/page/2/
    # 获取页面内容，状态
    beauty_url_list = []
    try:
        page_text, status = await aiohttp_get(session, beauty_url)
        logger.info(f"{beauty_url} |--> status:{status}")
        if status == 200:
            tree = etree.HTML(page_text)
            page_count_list = tree.xpath(
                "//ul[@class='uk-pagination uk-flex-center uk-margin-remove uk-visible@s']/li/a/text()")
            page_count = int(page_count_list[-1])
            for i in range(page_count):
                tmp_rul = "https://mmzztt.com/beauty/page/{}/".format(i + 1)
                beauty_url_list.append(tmp_rul)
    except Exception as e:
        import logging
        logger.error(e)
    finally:
        logger.info("All_beauty_page_urls: {}".format(beauty_url_list))
        return beauty_url_list


async def get_beauty_page_url_detail(session, beauty_page_url, logger, lock, txt_path):
    """
    根据beauty_page_url,获取每一页具体的信息,包含（创建时间、分类、名称、链接、编号）
    :param txt_path: 文件保存路径
    :param lock:
    :param session:
    :param beauty_page_url:
    :param logger:
    :return:
    """
    beauty_page_url_detail_list = []    # 返回列表
    try:
        fp = Path(txt_path)
        # 加锁 使用线程锁，保证数据安全
        lock.acquire()
        page_text, status = await aiohttp_get(session, beauty_page_url)
        # logger.info(f"{beauty_page_url} |--> status:{status}")
        if status == 200:
            tree = etree.HTML(page_text)
            # 当前页面数据条数 (//div[@class='uk-padding-small'])
            data_article_number = len(tree.xpath("(//div[@class='uk-padding-small'])"))
            for i in range(1, data_article_number + 1):
                # 每一个板块时间
                create_time = tree.xpath("(//div[@class='uk-padding-small'])[{}]/div/time/text()".format(i))[0]
                create_time = create_time.split(" ")[0]     # 只保留年月日
                # 对应分类名称
                forum_name = tree.xpath("(//div[@class='uk-padding-small'])[{}]/div/a/text()".format(i))[0]
                forum_name = forum_name.lstrip("#").rstrip("#")
                # 页面名称
                page_name = tree.xpath("(//div[@class='uk-padding-small'])[{}]/h2/a/text()".format(i))[0]
                page_name = my_tools.update_name(page_name)
                # 页面地址
                page_url = tree.xpath("(//div[@class='uk-padding-small'])[{}]/h2/a/@href".format(i))[0]
                # 页面编号
                page_number = page_url.split("/")[-1]
                tmp = (create_time, forum_name, page_name, page_number, page_url)
                # logger.info(tmp)
                beauty_page_url_detail_list.append(tmp)
                with open(fp.joinpath("beauty_name_url.txt"), "a+", encoding="utf-8") as f:
                    f.write(
                        forum_name + "|"  # 板块名称
                        + page_name + "|"  # 图片名称
                        + page_number + "|"  # 图片编号
                        + create_time + "|"  # 创建时间
                        + page_url + "\n"  # 图片地址
                    )
    except Exception as e:
        logger.error(e)
    finally:
        # 修改完成，释放锁
        lock.release()
        logger.info("页面：{} |-->  beauty_page_url_details: {}".format(beauty_page_url, beauty_page_url_detail_list))
        return beauty_page_url_detail_list
