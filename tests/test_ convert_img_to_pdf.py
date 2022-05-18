# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: test_ convert_img_to_pdf.py
@CreateTime: 2022/5/16 15:05
"""
from core import my_tools
from core.my_tools import ConvertImgToPdf, update_img_dpi
from PIL import Image
import os


if __name__ == '__main__':
    set_width = 1080
    filepath = "../res/test.jpeg"

    # """单张图片转pdf"""
    # output_path = "../res/test.pdf"
    # my_tools.ConvertImgToPdf(set_fixed_width=set_width).convert_img_pdf(filepath, output_path)
    #
    # """多张图片转pdf"""
    # folder_path = "../res/"
    # pdf_file_path_width = "../res/test_all_width.pdf"
    # pdf_file_path_height = "../res/test_all_height.pdf"
    # # set_height = 1660
    # ConvertImgToPdf(set_fixed_width=set_width).combine_imgs_pdf(folder_path, pdf_file_path_width)
    # # my_tools.ConvertImgToPdf(set_fixed_height=set_height).combine_imgs_pdf(folder_path, pdf_file_path_height)
    img_root_path = '../datas/images/tag/'
    # 保存路径
    save_path = '../datas/images/test/'
    name = "2022-05-15_66192_欲望都市_美女销售与VIP客户的秘密情事_81P_朱可儿"
    my_tools.mkdir(save_path + name)

    files = os.listdir(img_root_path + name)
    for file in files:
        new_file = "new_{}".format(file)
        update_file_path = img_root_path + name + "/" + file
        save_file_path = save_path + name + "/" + new_file
        # """更改图片dpi"""
        update_img_dpi(update_file_path=update_file_path, save_file_path=save_file_path, dpi_x=1200, dpi_y=1200)

    ConvertImgToPdf(set_fixed_width=3240).combine_imgs_pdf(save_path + name + "/", save_path + name + "/" + name + ".pdf")
