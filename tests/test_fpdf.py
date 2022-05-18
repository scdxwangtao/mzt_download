# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: test_fpdf.py
@CreateTime: 2022/5/16 17:44
"""
import os
from fpdf import FPDF

from core import my_tools

pdf = FPDF()
pdf.set_auto_page_break(False)  # 自动分页设为False

img_root_path = '../datas/images/tag/'
# 保存路径
save_path = '../datas/images/test/'
name = "2022-05-15_66192_欲望都市_美女销售与VIP客户的秘密情事_81P_朱可儿"
my_tools.mkdir(save_path + name)

files = os.listdir(img_root_path + name)

path = img_root_path + name + "/"
image_list = [i for i in os.listdir(path)]

for image in sorted(image_list):
    pdf.add_page()
    pdf.image(os.path.join(path, image), w=210, h=297)  # 指定宽高

# pdf.output(os.path.join(path, "/佩奇.pdf"), "F")
pdf.output(save_path + "test.pdf")
