# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: start.py
@CreateTime: 2022/5/7 19:12
"""
import asyncio
import threading
from pathlib import Path

import aiohttp
from aiohttp_socks import ProxyConnector
from python_socks import ProxyType

from core import forum_page, my_tools, detail_page, save_images
from logs.logger import MyLogger


class MZT:
    """程序入口，整个程序从此页面运行。"""

    def __init__(self):
        self.logger = MyLogger()  # 自定义日志
        self.lock = threading.RLock()  # 初始化线程锁
        # # 加锁   使用线程锁，保证数据安全
        # self.lock.acquire()
        # # 修改完成，释放锁
        # self.lock.release()
        self.referer = "https://mmzztt.com/"
        self.photo_url = "https://mmzztt.com/photo/tag/"  # 写真馆程序入口
        self.beauty_rul = "https://mmzztt.com/beauty/"  # 潮拍馆程序入口
        # Semaphore， 相当于基于服务器的处理速度和测试客户端的硬件条件，一批批的发
        # 直至发送完全部（下面定义的400）
        # 创建session，且对本地的TCP连接做限制limit=400（不做限制limit=0）
        # 超时时间指定
        # total:全部请求最终完成时间
        # connect: aiohttp从本机连接池里取出一个将要进行的请求的时间
        # sock_connect：单个请求连接到服务器的时间
        # sock_read：单个请求从服务器返回的时间
        self.semaphore = asyncio.Semaphore(16)  # 限制并发量
        self.timeout = aiohttp.ClientTimeout(total=3600 * 24, connect=60, sock_connect=60, sock_read=60)
        self.txt_path = "../datas/tmp_txt/"
        self.photo_save_path = '../datas/images/photo/'
        self.beauty_save_path = '../datas/images/beauty/'

        # 清空text_path文件夹
        my_tools.mkdir(self.txt_path, self.logger, is_delete=True)
        # 创建保存文件夹,不需要删除
        my_tools.mkdir(self.photo_save_path, self.logger)
        my_tools.mkdir(self.beauty_save_path, self.logger)

    async def photo_main(self):
        # connector = ProxyConnector(
        #     proxy_type=ProxyType.HTTP,
        #     host='127.0.0.1',
        #     port=10809,
        #     # username='user',
        #     # password='password',
        #     rdns=True,
        #     # ssl=False,
        #     # limit=32,
        # )

        # connector = ProxyConnector.from_url('https://127.0.0.1:10809')

        # async with aiohttp.ClientSession(connector=connector,   # 使用代理
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=32, ssl=False),  # 不使用代理
                                         timeout=self.timeout,
                                         headers=my_tools.get_headers(self.referer)) as session:
            # 获取小板块名称和链接
            forum_name_list = await forum_page.get_forum_name_list(session=session,
                                                                   forum_page_url=self.photo_url,
                                                                   logger=self.logger, )
            self.logger.info(forum_name_list)

            # 获取每个小板块的总页数和每一页链接
            # 建立所有任务
            page_tasks = [asyncio.create_task(forum_page.get_forum_page_list(session,
                                                                             forum_name,
                                                                             forum_url,
                                                                             self.semaphore,
                                                                             self.lock,
                                                                             self.txt_path,
                                                                             logger=self.logger, ))
                          for forum_name, forum_url in forum_name_list]

            # 触发await，等待任务完成
            # wait方法
            done, pending = await asyncio.wait(page_tasks)
            all_results = [done_task.result() for done_task in done]
            # 获取所有结果,结果保存在datas里边tag_all.txt
            # print("ALL RESULT:" + str(all_results))
            self.logger.info("ALL RESULT:" + str(all_results))

            # gather方法
            # all_results = await asyncio.gather(*page_tasks)
            # print(all_results)
            # self.logger.info(all_results)

            # 根据每一页链接，获取对应页面所有的图片链接标题等。
            # my_tools.read_file("../datas/tag_page.txt", "r")
            tag_page_list = my_tools.read_file(Path(self.txt_path).joinpath("tag_page.txt"), "r")
            tag_page_list = [s.split("|") for s in tag_page_list]
            # 建立name所有任务
            name_tasks = [asyncio.create_task(forum_page.get_detail_page_list(session,
                                                                              forum_name,
                                                                              forum_page_detail_url.rstrip("\n"),
                                                                              self.semaphore,
                                                                              self.lock,
                                                                              self.txt_path,
                                                                              logger=self.logger, ))
                          for forum_name, forum_page_detail_url in tag_page_list]
            # gather方法
            all_results = await asyncio.gather(*name_tasks)
            # print(all_results)
            self.logger.info(all_results)

            # 获取去重复后列表
            detail_page.list_de_weight(Path(self.txt_path), "tag_name.txt", logger=self.logger)
            # 读取本地文件自动去出分隔符|返回新列表
            new_de_weight_url_list = my_tools.get_new_list(self.txt_path, "de_weight_tag_name.txt")
            # 获取详情页面信息，保存到新文件
            # 创建获取详情页面的下载tasks
            detail_tasks = [asyncio.create_task(detail_page.get_detail_page_property(session=session,
                                                                                     forum_name=forum_name,
                                                                                     page_name=page_name,
                                                                                     page_create_time=page_create_time,
                                                                                     page_num=page_num,
                                                                                     page_count=page_count,
                                                                                     page_cover_rul=page_cover_rul,
                                                                                     detail_page_url=detail_page_url,
                                                                                     look=self.lock,
                                                                                     txt_path=self.txt_path,
                                                                                     logger=self.logger))
                            for forum_name, page_name, page_create_time, page_num, page_count, page_cover_rul,
                                detail_page_url in new_de_weight_url_list]
            # gather方法
            detail_all_results = await asyncio.gather(*detail_tasks)
            self.logger.info(detail_all_results)

            # 读取detail_message.txt,生成需要下载的列表
            detail_message_list = my_tools.get_new_list(self.txt_path, "detail_message.txt")
            # 获取每个名称对应的所有图片链接,并进行下载（同步下载）
            await detail_page.get_detail_img(referer=self.referer,
                                             session=session,
                                             semaphore=self.semaphore,
                                             save_img_path=self.photo_save_path,
                                             txt_path=self.txt_path,
                                             logger=self.logger,
                                             detail_message_list=detail_message_list)

    async def beauty_main(self):
        """潮拍馆 程序进入口：|--> https://mmzztt.com/beauty/  直接从最新标签开始获取"""
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=32, ssl=False),  # 不使用代理
                                         timeout=self.timeout,
                                         headers=my_tools.get_headers(self.referer)) as session:
            # 获取所有页面地址
            beauty_page_url_list = await forum_page.get_beauty_page_count_url_list(session=session,
                                                                                   beauty_url=self.beauty_rul,
                                                                                   logger=self.logger)

            # 根据beauty_page_url,获取每一页具体的信息
            # 建立所有任务
            beauty_detail_tasks = [asyncio.create_task(
                forum_page.get_beauty_page_url_detail(session=session,
                                                      beauty_page_url=beauty_page_url,
                                                      logger=self.logger,
                                                      lock=self.lock,
                                                      txt_path=self.txt_path))
                                                    for beauty_page_url in beauty_page_url_list]
            # gather方法
            beauty_detail_tasks_results = await asyncio.gather(*beauty_detail_tasks)
            self.logger.info(beauty_detail_tasks_results)

            # 根据上边步骤，将本地文件返回成列表
            beauty_detail_url_list = my_tools.get_new_list(self.txt_path, "beauty_name_url.txt")

            # 开始解析下载
            await detail_page.beauty_detail_page_resolution(referer=self.referer,
                                                            session=session,
                                                            semaphore=self.semaphore,
                                                            beauty_detail_url_list=beauty_detail_url_list,
                                                            dir_path=self.beauty_save_path,
                                                            txt_path=self.txt_path,
                                                            logger=self.logger,
                                                            lock=self.lock)


if __name__ == '__main__':
    mzt = MZT()
    try:
        '''DeprecationWarning: There is no current event loop
        loop = asyncio.get_event_loop() update to -->  loop = asyncio.new_event_loop()'''
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # loop.run_until_complete(mzt.photo_main())       # 写真馆启动程序
        loop.run_until_complete(mzt.beauty_main())  # 潮拍馆启动程序
    except Exception as e:
        mzt.logger.error(e)
