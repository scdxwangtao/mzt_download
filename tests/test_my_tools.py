# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: test_my_tools.py
@CreateTime: 2022/5/15 7:42
"""
from pathlib import Path
from core.my_tools import get_path_file_number, check_file_downloads, set_str_color, my_print


def test_get_path_file_number():
    dir_path = Path("../core")
    print(get_path_file_number(dir_path))
    print(7 != get_path_file_number(dir_path))
    print(7 != get_path_file_number(dir_path)["file_count"])
    print("file_count:{}".format(get_path_file_number(dir_path)["file_count"]))
    print("dir_count:{}".format(get_path_file_number(dir_path)["dir_count"]))


def test_check_file_downloads():
    file_num = 1        # 相差文件个数
    dir_path = Path("../datas/images/photo")
    txt_path = Path("../datas/tmp_txt")
    check_file_downloads(dir_path=dir_path, txt_path=txt_path, file_num=file_num, is_delete=True)


def test_set_str_color():
    print(set_str_color("测试字体颜色"))
    print(set_str_color("测试字体颜色", "black"))
    print(set_str_color("测试字体颜色", "red"))
    print(set_str_color("测试字体颜色", "green"))
    print(set_str_color("测试字体颜色", "yellow"))
    print(set_str_color("测试字体颜色", "blue"))
    print(set_str_color("测试字体颜色", "pink"))
    print(set_str_color("测试字体颜色", "cyan"))


def test_my_print():
    my_print("我的打印", "red")


if __name__ == '__main__':

    # test_get_path_file_number()

    test_check_file_downloads()

    # test_set_str_color()

    # test_my_print()
