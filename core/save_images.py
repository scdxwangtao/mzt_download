# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: save_images.py
@CreateTime: 2022/5/14 0:23
"""
import os
from pathlib import Path

from core import my_tools
from core.my_tools import my_print


async def down_img(session, path: str, img_url, semaphore, logger, is_cover=False):
    """下载图片"""
    # path = '../datas/images/tag/{}/'.format(detail_page_img_save_name)
    if is_cover:
        file_name = "000_cover_{}".format(img_url.split("/")[-1])
    else:
        file_name = img_url.split("/")[-1]
    my_tools.mkdir(path, logger)

    # 检查图片文件是否下载好了，不存在再进行下载。
    if not os.path.exists(f'{path}{file_name}'):
        async with semaphore:
            try:
                img = await session.get(img_url)
                status = img.status
                # logger.info(f'{path}{file_name} --> status:{status}')
                if status == 200:
                    # 触发到await就切换，等待get到数据
                    content = await img.read()
                    # 读取内容
                    with open(path + file_name, 'wb') as f:
                        # 写入至文件
                        f.write(content)
                        logger.info(f'{path}{file_name} 下载完成！')
                    return str(img_url)
            except Exception as e:
                logger.error(e)
                # 失败后再次调用
                await down_img(session, path, img_url, semaphore, logger, is_cover=False)
                # return str(img_url)
    else:
        logger.info(f'{path}{file_name} 已存在，不需要下载！')
        return str(img_url)


def get_cover_dir_rul_list(save_path, txt_path):
    """获取封面图保存地址和url列表"""
    urls = my_tools.read_file(Path(txt_path).joinpath("tag_name.txt"), "r")
    dirs = os.listdir(Path(save_path))
    dir_url_list = []
    tmp = []
    de_weight_nums = []

    # 去重
    for num_url in urls:
        num_url = num_url.split("|")
        num = num_url[3]
        url = num_url[5]
        if num not in tmp:
            tmp.append(num)
            de_weight_nums.append((num, url))
    my_print("原始数据共：{}条".format(len(urls)), "yellow")
    my_print("去重后始数据共：{}条".format(len(tmp)), "green")

    # 添加去重后地址
    for num_url in de_weight_nums:
        num = num_url[0]
        url = num_url[1]
        for cover_dir in dirs:
            if num in cover_dir:
                dir_url_list.append((cover_dir, url))
                break
    return dir_url_list
