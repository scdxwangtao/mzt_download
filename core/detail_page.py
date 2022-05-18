# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: detail_page.py
@CreateTime: 2022/5/13 23:21
"""

import asyncio
import os
import random
import shutil
import tempfile
from pathlib import Path

from lxml import etree
from pyppeteer_stealth import stealth
from core import my_browser, my_tools, save_images
from core.my_tools import check_file_downloads, my_print


def list_de_weight(path, file_name, logger):
    """列表数据去重复，生成不重复的列表文件"""
    url_list = my_tools.read_file(path.joinpath(file_name), "r")
    tmp = []
    de_weight_url_list = []
    for img_details in url_list:
        img_details = img_details.split("|")
        detail_page_img_save_number = int(img_details[3])
        # 去除重复的链接
        if detail_page_img_save_number not in tmp:
            tmp.append(detail_page_img_save_number)
            de_weight_url_list.append(img_details)
    logger.info("共有{}个不重复页面。".format(len(de_weight_url_list)))
    count = 0
    for url_list in de_weight_url_list:
        forum_name = url_list[0]
        page_name = url_list[1]
        page_time = url_list[2]
        page_number = url_list[3]
        page_count = url_list[4]
        cover_rul = url_list[5]
        page_url = url_list[6]
        count += int(page_count)
        with open(path.joinpath("de_weight_tag_name.txt"), "a+", encoding="utf-8") as f:
            f.write(forum_name + "|"
                    + page_name + "|"
                    + page_time + "|"
                    + page_number + "|"
                    + page_count + "|"
                    + cover_rul + "|"
                    + page_url + "\n")
    logger.info("共有{}张图片。".format(count))
    return de_weight_url_list


async def get_detail_img(referer, session, semaphore, save_img_path, txt_path, logger, detail_message_list):
    browser = await my_browser.get_browser(logger)
    detail_img_list_all = []
    fp = Path(txt_path)

    # 检查文件夹中相差比较大的文件夹，判断是否下载完全，没下载完全的删除。
    logger.info(check_file_downloads(dir_path=Path(save_img_path), txt_path=Path(txt_path), file_num=2, is_delete=True))

    """
    f.write(forum_name.rstrip("\n") + "|"
                            + page_name.rstrip("\n") + "|"
                            + page_number.rstrip("\n") + "|"
                            + page_count.rstrip("\n") + "|"
                            + page_url.rstrip("\n") + "|"
                            + page_create_time + "|"
                            + model_name.rstrip("\n") + "|"
                            + page_describe.rstrip("\n") + "|"
                            + page_cover_rul.rstrip("\n") + "|"
                            + page_tag_list + "\n")"""

    for img_details in detail_message_list:
        detail_page_forum_name = img_details[0]  # 板块名称
        detail_page_img_save_name = img_details[1]  # 保存文件夹名称
        detail_page_img_save_number = int(img_details[2])  # 图片编号
        detail_page_img_count = int(img_details[3])  # 图片总数
        detail_page_img_url = img_details[4].rstrip("\n")  # 图片地址
        detail_page_time = img_details[5]  # 图片日期
        detail_page_model_name = img_details[6]  # 获取模特名字
        detail_page_describe = img_details[7]  # 页面描述
        detail_page_cover_url = img_details[8]  # 图片封面地址
        detail_page_tag_list = img_details[9]  # 图片所含标签
        page_count = detail_page_img_count  # 固定图片总数

        logger.info("当前下载页面板块为：{} 当前下载页面名称为：{} 总共有{}页图片，地址为：{} 保存编号为：{} 模特名字为：{}".format(
            detail_page_forum_name,
            detail_page_img_save_name,
            detail_page_img_count,
            detail_page_img_url,
            detail_page_img_save_number,
            detail_page_model_name))

        # 保存地址
        save_path = save_img_path + "{}_{}_".format(detail_page_time, detail_page_img_save_number) + \
                    detail_page_img_save_name + "_{}P_{}/".format(page_count, detail_page_model_name)
        logger.info(my_tools.set_str_color("save_path:{}".format(save_path), "yellow"))
        if not os.path.exists(Path(save_path).joinpath("000_cover_960.jpg")):
            # 下载封面
            try:
                await save_images.down_img(session=session,
                                           path=save_path,
                                           img_url=detail_page_cover_url,
                                           semaphore=semaphore,
                                           logger=logger,
                                           is_cover=True)
                logger.info("{} 封面下载成功！".format(Path(save_path).joinpath("000_cover_960.jpg")))
            except Exception as e:
                logger.error(e)
        else:
            logger.warning("{} 封面已经下载成功！不需要再次下载".format(Path(save_path).joinpath("000_cover_960.jpg")))

        try:
            # 判断需要下载的文件名称是否存在，不存在才进行下载。
            if not os.path.exists(save_path):
                await detail_page_resolution(browser, detail_page_img_url, referer, detail_page_img_count, fp, logger,
                                             detail_page_forum_name, detail_page_img_save_name, detail_page_time,
                                             page_count, detail_page_img_save_number, session, save_path, semaphore,
                                             detail_img_list_all)
            else:
                logger.warning("文件{}已存在！".format(save_path))
                file_count = my_tools.get_path_file_number(Path(save_path))["file_count"]
                if page_count > file_count:  # 如果获取到的总页数大于已经下载的文件总数，表示文件没下载完全，重新下载
                    if file_count == 1:  # 表示先下载的封面文件。
                        logger.info("此文件{}只下载了封面不需要删除，继续下载文件。".format(save_path))
                    else:
                        logger.warning("文件{}未下载完全，删除后重新下载！".format(save_path))
                        my_tools.mkdir(save_path, logger=logger, is_delete=True)  # 删除并重新创建文件夹
                    await detail_page_resolution(browser, detail_page_img_url, referer, detail_page_img_count, fp,
                                                 logger, detail_page_forum_name, detail_page_img_save_name,
                                                 detail_page_time, page_count, detail_page_img_save_number, session,
                                                 save_path, semaphore, detail_img_list_all)
                else:
                    logger.warning('文件{}已存在,并下载完全！'.format(save_path))
        except Exception as e:
            logger.error(e)
        finally:
            pass
    await browser.close()  # 关闭浏览器对象
    return detail_img_list_all


async def detail_page_resolution(browser, detail_page_img_url, referer, detail_page_img_count, fp, logger,
                                 detail_page_forum_name, detail_page_img_save_name, detail_page_time, page_count,
                                 detail_page_img_save_number, session, save_path, semaphore, detail_img_list_all):
    """详情页面解析方法，配合get_detail_img方法使用"""
    while True:
        try:
            page_response = await my_browser.get_page(browser, url=detail_page_img_url, referer=referer)
            page = page_response[0]
            response = page_response[1]
            resp_status = response.status  # 响应状态
            if resp_status == 200:
                break
            else:
                continue
        except Exception as e:
            logger.error(e)
            return
    # await stealth(page)  # <-- 防止机器人检查
    detail_page_url_num = random.randint(10, 15)
    index_page = 1  # 第一张图片
    while detail_page_img_count > 0:
        # 获取第一页的数据
        page_text = await page.content()  # 获取页面内容
        await asyncio.sleep(random.uniform(0.4, 0.6))  # 等待随机秒，根据网络情况调整
        # print(page_text)
        tree = etree.HTML(page_text)
        img_title = ''
        img_url = ''
        try:
            img_title = tree.xpath("//h1[@class='uk-article-title uk-text-truncate']/text()")[0]
            img_title = my_tools.update_name(img_title)
            img_url = tree.xpath("//figure/img/@src")[0]
        except Exception as e:
            print(e)
            continue
        logger.info("{}： 正在获取第{}页的数据".format(img_title, index_page))
        logger.info(img_title + ":  " + img_url)
        # 保存链接
        with open(fp.joinpath("tag_img_urls.txt"), "a+", encoding="utf-8") as f:
            f.write(detail_page_forum_name + "|"
                    + detail_page_img_save_name + "|"
                    + detail_page_time + "|"
                    + img_title + "|"
                    + str(page_count) + "|"
                    + str(detail_page_img_save_number) + "|"
                    + img_url + "\n")
        tmp_url = detail_page_forum_name, \
                  detail_page_img_save_name, \
                  detail_page_time, \
                  page_count, \
                  detail_page_img_save_number, \
                  img_title, \
                  img_url
        # 进行下载
        await save_images.down_img(
            session=session,
            path=save_path,
            img_url=img_url,
            semaphore=semaphore,
            logger=logger,
            is_cover=False)
        # 添加到列表
        detail_img_list_all.append(tmp_url)

        logger.info('{}:已经下载了{}条数据！'.format(img_title, index_page))
        index_page += 1
        detail_page_img_count -= 1
        if index_page % detail_page_url_num == 0:
            sleet_time = random.uniform(1.0, 1.5)
            # 绿色高亮显示
            logger.info("{}:已经下载了{}条数据。暂停{}秒继续下载。".format(img_title, index_page, round(sleet_time, 2)))
            await asyncio.sleep(sleet_time)

        rul_count = my_tools.count_lines(fp.joinpath("tag_img_urls.txt"), )
        logger.info('程序一共已经下载了{}条数据！'.format(rul_count))

        # 第一种写法
        await page.waitForSelector('.uk-position-center-right', {'timeout': 60 * 1000})
        # await asyncio.sleep(random.uniform(0.1, 0.15))  # 等待随机秒，根据网络情况调整
        # await asyncio.sleep(random.uniform(0.3, 0.5))  # 等待随机秒，根据网络情况调整
        await asyncio.sleep(random.uniform(0.4, 0.6))  # 等待随机秒，根据网络情况调整
        await page.click(".uk-position-center-right")  # 点击

        # # 第二种写法， 报错
        # await asyncio.gather(
        #     page.waitForNavigation({'timeout': 100}),
        #     page.click(".uk-position-center-right")  # 点击
        # )

        # # 第三种写法
        # await asyncio.wait([
        #     page.waitForNavigation({'timeout': random.uniform(0.1, 0.15) * 1000}),
        #     page.click(".uk-position-center-right"),  # 点击
        # ])


async def get_detail_page_property(session, forum_name, page_name, page_create_time, page_num, page_count,
                                   page_cover_rul, detail_page_url, look, txt_path, logger):
    """
    获取页面详情页面信息
    :param logger:
    :param session:  aiohttp session
    :param forum_name: 板块名称
    :param page_name:   页面名称
    :param page_create_time:    页面创建时间
    :param page_num:    页面编号
    :param page_count:  页面共有多少张图片
    :param page_cover_rul:  页面封面地址
    :param detail_page_url: 页面进入地址
    :param look:    线程锁
    :param txt_path:    保存文件路径
    :return:    返回详细信息元组
    """
    forum_name = forum_name  # 板块名称
    page_url = detail_page_url  # 页面地址
    page_cover_rul = page_cover_rul  # 页面封面地址
    page_number = page_num  # 页面编号
    page_name = page_name  # 页面标题
    page_count = page_count  # 文件数
    model_name = "佚名"  # 模特名字
    page_describe = "没有描述"  # 页面描述
    page_tag_list = []  # 页面包含标签
    page_create_time = page_create_time  # 页面创建时间
    while True:
        try:
            # 加锁  使用线程锁，保证数据安全
            look.acquire()
            response, status = await my_tools.aiohttp_get(session, detail_page_url)
            if status == 200:
                model_tree = etree.HTML(response)
                # 获取模特名字
                model_name_list = model_tree.xpath("//a[@class='uk-button uk-button-text uk-text-lead']/text()")
                if len(model_name_list) != 0:
                    model_name = model_name_list[0]
                # 获取描述
                page_describe_list = model_tree.xpath("//p[@class='u-desc']/text()")
                if len(page_describe_list) != 0:
                    page_describe = page_describe_list[0]
                # 获取当前页面包含标签
                page_tag_list = str(model_tree.xpath("(//div[@class='uk-card-body'])[1]/button/a/text()"))
                # 保存
                with open(Path(txt_path).joinpath("detail_message.txt"), "a+", encoding="utf-8") as f:
                    f.write(forum_name.rstrip("\n") + "|"
                            + page_name.rstrip("\n") + "|"
                            + page_number.rstrip("\n") + "|"
                            + page_count.rstrip("\n") + "|"
                            + page_url.rstrip("\n") + "|"
                            + page_create_time + "|"
                            + model_name.rstrip("\n") + "|"
                            + page_describe.rstrip("\n") + "|"
                            + page_cover_rul.rstrip("\n") + "|"
                            + page_tag_list + "\n")
            else:
                logger.warning(status)
                continue
        except Exception as e:
            logger.error(e)
            continue
        finally:
            # 修改完成，释放锁
            look.release()
            # 返回元组
            tmp_tup = (forum_name, page_name, page_number, page_count, page_url, page_create_time, model_name,
                       page_describe, page_cover_rul, page_tag_list)
            return tmp_tup


async def beauty_detail_page_resolution(referer, session, semaphore, beauty_detail_url_list, dir_path, txt_path,
                                        logger, lock):
    """
    beauty模块解析下载方法
    :param referer:
    :param session:
    :param semaphore:
    :param beauty_detail_url_list:
    :param dir_path:
    :param txt_path:
    :param logger:
    :param lock:
    :return:
    """
    browser = await my_browser.get_browser(logger)
    new_beauty_detail_url_list = []
    down_num_list = []

    logger.info(my_tools.set_str_color("一共有{}个文件夹需要下载。".format(len(beauty_detail_url_list)), "pink"))
    # 下载前先获取指定根路径下有哪些文件夹。检查哪些是完全下载好了的。
    folders = os.listdir(dir_path)
    for folder in folders:
        if folder.endswith("P"):  # 文件夹以P结尾的表示下载完全了的。
            page_count = int(folder.split("_")[-1].rstrip("P"))
            file_count = len(os.listdir(dir_path + folder))
            if page_count == file_count:  # 表示下载完全。
                down_num = folder.split("_")[2]  # 下载完成的图片编号
                down_num_list.append(down_num)
            else:
                logger.info(my_tools.set_str_color("当前文件：{}未下载完全，差{}张图片未下载，已删除。"
                                                   .format(folder, page_count - file_count), "red"))
                shutil.rmtree(dir_path + folder)  # 直接删除
        else:
            logger.info(my_tools.set_str_color("当前文件：{}未下载完全，直接删除。".format(folder), "red"))
            shutil.rmtree(dir_path + folder)  # 直接删除
    logger.info(my_tools.set_str_color("已完全下载{}个文件夹的文件。".format(len(down_num_list)), "green"))

    # 获取未下载链接。
    for beauty_detail_url in beauty_detail_url_list:
        page_number = beauty_detail_url[2]
        # 检查当前num，是否在已下载列表中，如不在，则添加beauty_detail_url
        if page_number not in down_num_list:
            new_beauty_detail_url_list.append(beauty_detail_url)
    logger.info(my_tools.set_str_color("还有{}个文件夹的文件没有下载。".format(len(new_beauty_detail_url_list)), "yellow"))

    # 读取新链接进行下载
    for beauty_detail_url in new_beauty_detail_url_list:
        forum_name = beauty_detail_url[0]
        page_name = beauty_detail_url[1]
        page_number = beauty_detail_url[2]
        create_time = beauty_detail_url[3]
        page_url = beauty_detail_url[4]

        # 再次查看文件是否存在，不存在再下载
        await beauty_exists_download(browser, referer, session, semaphore, dir_path, txt_path, logger, lock, forum_name,
                                     page_name, page_number, create_time, page_url, sleep_times=3.0)

    await browser.close()  # 所有下载完成后，关闭浏览器对象


async def beauty_exists_download(browser, referer, session, semaphore, dir_path, txt_path, logger, lock, forum_name,
                                 page_name, page_number, create_time, page_url, sleep_times=1.0):
    save_name = "{}_{}_{}_{}".format(forum_name, create_time, page_number, page_name)
    dir_save_path = dir_path + save_name + "/"
    fp = Path(txt_path)

    if not os.path.exists(dir_save_path):  # 判断文件夹是否存在
        page_response = await my_browser.get_page(browser, url=page_url, referer=referer)
        page = page_response[0]
        response = page_response[1]
        resp_status = response.status  # 响应状态
        if resp_status == 200:
            detail_page_url_num = random.randint(10, 15)
            index_page = 1  # 第一张图片
            tmp_img_title = ""  # 第一页标题
            contrast_title = ""  # 做对比的标题
            while True:
                page_text = await page.content()  # 获取页面内容
                # 点击后等待随机秒，根据网络情况调整sleep_times,等待页面加载完成。
                await asyncio.sleep(random.uniform(0.4 * sleep_times, 0.7 * sleep_times))
                tree = etree.HTML(page_text)
                try:
                    img_title = tree.xpath("//h1[@class='uk-article-title uk-text-truncate']/text()")[0]
                    img_title = my_tools.update_name(img_title.split("(")[0])       # 保留括号前边部分
                    img_url = tree.xpath("//figure/img/@src")[0]
                    logger.info("{}： 正在获取第{}页的数据".format(page_name, index_page))
                    logger.info(img_title + ":  " + img_url)
                    if index_page == 1:  # 第一次进入修改标题，后边不修改
                        tmp_img_title = img_title  # 标题第一页的去除括号后边部分。
                        contrast_title = img_title
                        logger.info("第{}页{}".format(index_page, contrast_title))
                    else:
                        # 如果标题是以第一页标题开始的，表示还在当前当前页面
                        if img_title.startswith(tmp_img_title):
                            contrast_title = img_title
                            logger.info("第{}页{}".format(index_page, contrast_title))
                        else:
                            try:
                                page_count = int(contrast_title.split("_")[-2])
                            except Exception as e:
                                page_count = 1
                                logger.error(e)
                                logger.warning("此目录只有一张图片。")
                            # 如果标题不是以第一页标题开始的，表示已经下载完全,退出当前下载
                            # 当前标题总页面数，保存到本地
                            sleet_time = round(random.uniform(1 * sleep_times, 2.0 * sleep_times), 2)
                            logger.warning("等待下载完全，暂停{}秒继续下载。".format(sleet_time))
                            await asyncio.sleep(sleet_time)
                            files = os.listdir(dir_save_path)
                            if page_count > len(files):
                                logger.warning(my_tools.set_str_color(
                                    "图片名称：{}，地址：{}， 没有下载完。差{}张图片未下载。删除后下次重新下载！！"
                                    .format(page_name, page_url, page_count - len(files)), "red"))
                                break  # 下载失败先不管了。
                            else:
                                logger.info(my_tools.set_str_color("图片一共有{}张， 名称：{}，地址：{}， 已完成下载成功！！！。"
                                                                   .format(page_count, page_name, page_url), "yellow"))
                                os.rename(dir_save_path, dir_save_path.rstrip("/") + "_{}P".format(page_count))
                                break
                    # 保存链接到本地
                    # 加锁 使用线程锁，保证数据安全
                    lock.acquire()
                    with open(fp.joinpath("beauty_img_urls.txt"), "a+", encoding="utf-8") as f:
                        f.write(save_name + "|"
                                + page_url.rstrip("\n") + "|"
                                + img_url + "\n")
                    # 修改完成，释放锁
                    lock.release()

                    # 保存图片
                    await save_images.down_img(session=session, path=dir_save_path, img_url=img_url,
                                               semaphore=semaphore, logger=logger)
                    # 检查状态
                    await chick_download_status(logger, page_name, index_page, detail_page_url_num, fp, sleep_times)
                    # 模拟点击
                    await await_click(page=page, sleep_times=sleep_times)
                    # 修改页数
                    index_page += 1

                except Exception as e:
                    print(e)
                    logger.error(e)
                    continue


async def chick_download_status(logger, page_name, index_page, detail_page_url_num, fp, sleep_times):
    """
    检查当前程序当前页面获取状态。和总下载状态
    :param fp:      txt_path
    :param logger:
    :param page_name:
    :param index_page:
    :param detail_page_url_num:
    :param sleep_times:
    :return:
    """
    logger.info(my_tools.set_str_color('{}:已经下载了{}条数据！'.format(page_name, index_page), "cyan"))

    if index_page % detail_page_url_num == 0:
        sleet_time = random.uniform(0.5 * sleep_times, 1.0 * sleep_times)
        # 绿色高亮显示
        logger.info(my_tools.set_str_color("{}:已经下载了{}条数据。暂停{}秒继续下载".format(page_name,
                                                                            index_page,
                                                                            round(sleet_time, 2)),
                                           "green"))
        await asyncio.sleep(sleet_time)

    rul_count = my_tools.count_lines(fp.joinpath("beauty_img_urls.txt"), )
    logger.info(my_tools.set_str_color("当前程序启动后一共已经下载了{}条数据！".format(rul_count), "pink"))


async def await_click(page, sleep_times):
    """
    页面等待点击
    :param page:
    :param sleep_times: 等待倍数
    :return:
    """
    await page.waitForSelector('.uk-position-center-right', {'timeout': 60 * 1000})
    # await asyncio.sleep(random.uniform(0.3 * sleep_times, 0.5 * sleep_times))  # 等待随机秒，根据网络情况调整
    # await asyncio.sleep(random.uniform(1.0, 1.6))  # 等待随机秒，根据网络情况调整,下载大文件
    await page.click(".uk-position-center-right")  # 点击
