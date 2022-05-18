# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: test_save_images.py
@CreateTime: 2022/5/14 0:36
"""
import asyncio
from pathlib import Path

import aiohttp

from core import save_images, my_tools
from core.save_images import get_cover_dir_rul_list


async def test_down_img():
    # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=4, ssl=False),
    #                                  headers=my_tools.get_headers(referer)) as session:

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=4, loop=loop),
                                     # trust_env=True,
                                     headers=my_tools.get_headers(referer)) as session:
        path = '../datas/images/{}/'.format("test")

        # 多个任务
        tasks = [asyncio.create_task(save_images.down_img(session, path, img_url, semaphore)) for img_url in img_urls]
        all_results = await asyncio.gather(*tasks)
        print(all_results)

        # # # 单个任务
        # await save_images.down_img(session, path, one_img_url, semaphore)


def test_get_cover_dir_rul_list(save_path, txt_path):
    dir_rul_list = get_cover_dir_rul_list(save_path=save_path, txt_path=txt_path)
    my_tools.my_print(dir_rul_list, "cyan")


async def test_down_cover(referer, save_img_path, save_path, cover_url, semaphore):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=32, ssl=False),  # 不使用代理
                                     # timeout=self.timeout,
                                     headers=my_tools.get_headers(referer)) as session:
        await save_images.down_img(session=session,
                                   path=save_img_path + save_path + "/",
                                   img_url=cover_url,
                                   semaphore=semaphore,
                                   is_cover=True)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    referer = "https://mmzztt.com/"
    save_img_path = '../datas/images/tag/'
    txt_path = "../datas/tmp_txt/"
    save_path = "2021-09-14_39752_翘臀美女最性感_丰满尤物小海臀丰胸翘臀姿势妖娆_50P_小海臀"
    cover_url = 'https://s.iimzt.com/thumb/39752/960.jpg'
    semaphore = asyncio.Semaphore(4)  # 限制并发量

    # one_img_url = "https://p.iimzt.com/2022/02/15f40e.jpg"
    # img_urls = ["https://p.iimzt.com/2022/02/15f40e.jpg",
    #             "https://p.iimzt.com/2021/12/04a30f.jpg",
    #             "https://p.iimzt.com/2022/02/15f41c.jpg",
    #             "https://p.iimzt.com/2022/02/15f43d.jpg",
    #             "https://p.iimzt.com/2022/02/15f44d.jpg",
    #             "https://p.iimzt.com/2022/02/15f46f.jpg",
    #             "https://p.iimzt.com/2022/02/08c08a.jpg",
    #             "https://p.iimzt.com/2022/02/08c06b.jpg",
    #             "https://p.iimzt.com/2022/02/08c12e.jpg",
    #             "https://p.iimzt.com/2022/02/08c15c.jpg",
    #             "https://p.iimzt.com/2022/02/08c16e.jpg",
    #             "https://p.iimzt.com/2022/02/08c20f.jpg",
    #             "https://p.iimzt.com/2022/02/08c22c.jpg",
    #             "https://p.iimzt.com/2022/02/08c23a.jpg",
    #             ]
    # loop.run_until_complete(test_down_img())

    test_get_cover_dir_rul_list(save_path=save_img_path, txt_path=txt_path)
    # loop.run_until_complete(test_down_cover(referer, save_img_path, save_path, cover_url, semaphore))


