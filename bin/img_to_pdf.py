# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: img_to_pdf.py
@CreateTime: 2022/5/16 15:29
"""
import os
from pathlib import Path

from core import my_tools
from core.my_tools import ConvertImgToPdf, imgs_to_pdf_more_folder

if __name__ == '__main__':
    # 需要合成路径
    img_root_path = '../datas/images/photo/'
    # 保存路径
    save_path = r"E:/mzt_pdf/"

    # 单个文件合成
    # name = "2022-05-15_66192_欲望都市_美女销售与VIP客户的秘密情事_81P_朱可儿"
    # folder_path = img_root_path + name + "/"
    # ConvertImgToPdf(set_fixed_width=3240).combine_imgs_pdf(folder_path,
    #                                                        str(Path(img_root_path).joinpath(name + ".pdf")))

    # 多个同时合成
    imgs_to_pdf_more_folder(img_root_path=img_root_path, save_path=save_path)
