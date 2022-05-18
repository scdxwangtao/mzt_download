# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: test_delete_cover.py
@CreateTime: 2022/5/16 15:42
"""
from core.my_tools import delete_cover_img


if __name__ == '__main__':
    # 从根路径删除多个封面
    delete_img_path = '../datas/images/tag/'
    cover_name = "cover_960.jpg"
    delete_cover_img(delete_img_path, cover_name)
