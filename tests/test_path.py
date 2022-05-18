# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: test_path.py
@CreateTime: 2022/5/12 14:19
"""
import os
from os import path  # python3.4之前使用这种方式
from pathlib import Path  # python3.4建议使用这种方式

dirs = "../datas"
files = os.listdir(dirs)   # 读入文件夹
num_png = len(files)       # 统计文件夹中的文件个数
print(num_png)             # 打印文件个数

a = "123"
print(a.join(("456", "789", "111")))

p = path.join('/etc', 'sysconfig', 'network')
print(type(p), p)  # p的类型是字符串
print(path.exists(p))

print(path.split(p))  # 类型是元组;分割的结果为路径和基名
print(path.split('c:/test/a/b.txt'))  # ('c:/test/a', 'b.txt')，最后一部分为basename基名
print(path.dirname('c:/test/a/b.tar.gz'))  # linux中对于路径中的冒号，会将其认为是合法的文件名称
print(path.abspath('.'))  # 当前目录的绝对路径
print(path.abspath(''))  # 同样是当前目录的绝对路径
print(__file__)  # 当前路径下的当前文件

p1 = '/a/b/c/d/e/f/g.tar.gz'  # 打印p1的所有父目录

parent = path.dirname(p1)
print(parent)
while parent != path.dirname(parent):
    parent = path.dirname(parent)
    print(parent)

p2 = Path()  # 创建了一个路径对象
print(p2)  # 结果为点.，默认为当前路径
print(p2.absolute())

print(Path())  # 三种方式都是当前路径
# print(Path('.'))
# print(Path(''))

p3 = Path('/etc', 'sysconfig', 'network')
print(p3)

p4 = Path('a/b', 'c', 'd/e')
print(p4)

p5 = Path(p3, p4)
print(p5)

print(p5 / 'f' / 'g/h' / '123.zip')

# 总结：Path / str, str / Path, Path / Path 三种方式拼接结果都是路径对象
