# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: my_tools.py
@CreateTime: 2022/5/7 19:26
"""
import random
import ssl
import time
from datetime import datetime
from pathlib import Path

import requests
import win32con
import win32gui
import win32print
from fake_useragent import UserAgent  # pip install fake-useragent
from requests.adapters import HTTPAdapter
from win32api import GetSystemMetrics
import shutil
import os
from PIL import Image  # pip install pillow
import pandas


def get_local_conf_user_agent():
    """通过读取本地user_agents文件，获取随机的user_agent"""
    fp = Path('../conf/user_agents.csv')
    house_info = pandas.read_csv(fp)
    tmp = random.randint(0, len(house_info) - 1)
    user_agent = house_info.loc[tmp]["ua"]
    # print(house_info.loc[tmp]["id"])
    # print(house_info.loc[tmp]["ua"])
    return user_agent


def get_headers(referer=None):
    # ua = UserAgent()
    headers = {
        # Random generation User-Agent
        # 'User-Agent': ua.random,
        'User-Agent': get_local_conf_user_agent(),
        # 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        #               "Chrome/101.0.4951.54 Safari/537.36",
        "Referer": referer,
        "date": datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'),
        # "Connection": "close",  # requests默认是keep-alive的，可能没有释放，加参数 headers={'Connection':'close'}
        # "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        # "sec-ch-ua-mobile": "?0",
        # "sec-ch-ua-platform": "Windows",
    }
    return headers


def get_url(url, referer=None, proxies=None):
    """
    Method to get the response page
    :param url: indicates the address of the page to be obtained.
    :param referer: The HTTP Referer is part of the header. When a browser sends a request to a Web server,
            it usually carries the Referer with it to tell the server from which page the web page is linked,
            so that the server can obtain some information for processing.
    :param proxies: proxies = {'http': "https://127.0.0.1:10809"} or proxies = {'http': "127.0.0.1:10809"}
    :return response the retrieved response content.
    """

    # Ignore certificate validation warnings。
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = get_headers(referer=referer)
    # ('Connection broken: IncompleteRead(0 bytes read)', IncompleteRead(0 bytes read))
    my_session = requests.Session()
    # # max_retries 为最大重试次数，重试5次，加上最初的一次请求，一共是6次
    # my_session.mount('http://', HTTPAdapter(max_retries=5))
    # my_session.mount('https://', HTTPAdapter(max_retries=5))
    # 增加连接重试次数
    requests.adapters.DEFAULT_RETRIES = 5
    # 关闭多余连接
    my_session.keep_alive = False
    try:
        response = my_session.get(url=url,
                                  headers=headers,
                                  # stream=True   requests.exceptions.ChunkedEncodingError:
                                  stream=True,
                                  timeout=(300, 300),  # 设置超时时间，前边为请求时间，后边为响应时间
                                  proxies={'https': proxies},  # 设置代理
                                  # 关闭后提示： InsecureRequestWarning: Unverified HTTPS request is being made to host
                                  verify=False,  # 关闭 SSL 验证 ，关了部分数据下载0kb
                                  )
        if response.status_code == 200:
            return response
    except requests.exceptions.RequestException as e:
        print(e)
        return
    finally:
        my_session.close()


async def aiohttp_get(session, url):
    async with session.get(url) as response:
        return await response.text(), response.status


def get_real_resolution():
    """获取真实的分辨率"""
    h_dc = win32gui.GetDC(0)
    # 横向分辨率
    w = win32print.GetDeviceCaps(h_dc, win32con.DESKTOPHORZRES)
    # 纵向分辨率
    h = win32print.GetDeviceCaps(h_dc, win32con.DESKTOPVERTRES)
    return w, h


def get_screen_size():
    """获取缩放后的分辨率"""
    w = GetSystemMetrics(0)
    h = GetSystemMetrics(1)
    return w, h


def get_scaling():
    """获取缩放比例"""
    real_resolution = get_real_resolution()
    screen_size = get_screen_size()
    scaling = round(real_resolution[0] / screen_size[0], 2)
    return scaling


async def set_page(my_page):  # 传入要设置的页面对象即可
    width, height = get_screen_size()
    await my_page.setViewport({'width': width, 'height': height})
    # # 如果这一条报错则使用下一条
    # await my_page.evaluateOnNewDocument('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')
    await my_page.evaluateOnNewDocument(
        'function(){Object.defineProperty(navigator, "webdriver", {get: () => undefined})}')


def mkdir(path, logger, is_delete=False):
    """
    Method to create a new subdirectory
    :param logger: 日志对象
    :param is_delete: Whether or not to delete
    :param path:  The address to create the folder
    :return: Boolean
    """
    # Remove the leading space and then the trailing \ symbol.
    path = path.strip().rstrip("\\")

    # Check whether a path exists。True for existence and False for nonexistence.
    is_exists = os.path.exists(path)

    if not is_exists:
        # If the directory address does not exist, create the directory.
        try:
            os.makedirs(path)
            logger.info("directory:" + path + ' Creating a successful!')
            return True
        except Exception as e:
            logger.error("directory:" + path + ' Create a failure！')
            logger.error(e)
            return False
    else:
        # If the directory exists, it is not created and a message
        # is displayed indicating that the directory already exists.
        logger.info("directory:" + path + ' the directory already exists！')
        try:
            # delete the original directory.
            if is_delete:
                shutil.rmtree(path)
                logger.info("The original directory has been deleted.")
                # Create the directory again.
                try:
                    os.makedirs(path)
                    logger.info("directory:" + path + ' Succeeded in creating the directory again!')
                    return True
                except Exception as e:
                    logger.error("directory:" + path + ' Failure in creating the directory again！')
                    logger.error(e)
                    return False
            else:
                logger.warning("Directories do not need to be deleted.")
        except Exception as e:
            logger.error("Failed to delete the original directory.")
            logger.error(e)


def update_name(name):
    """
    The method of updating the name
    :param name: The name you want to change.
    :return: Modified name
    """
    chinese_symbols = "~·！@#￥%……&*（）——+-={}【】|、：；“‘《》，。？/"
    english_symbols = "~`!@#$%^&*()+-/=|\\[]{};:'\"<,>.? "
    string = chinese_symbols + english_symbols
    # Check if the string contains any of the special symbols listed above and replace them with "_"
    for i in string:
        if i in name:
            # Replace special characters
            # name = name.replace(i, "_").replace("__", "_").replace("___", "_").replace("____", "_")
            name = name.replace(i, "_")
    return name


def count_lines(file_path):
    """
    Gets the number of lines of the current file by passing in the file address
    :param file_path:
    :return:
    """
    count = -1
    for count, line in enumerate(open(file_path, 'rU', errors="ignore")):
        pass
    count += 1
    return count


def get_all_files(path):
    """
    Get all the addresses
    :param path:    root path
    :return: all file path and name
    """
    all_file = []
    for dir_path, dir_names, filenames in os.walk(path):
        for dir_ in dir_names:
            all_file.append(os.path.join(dir_path, dir_))
        for name in filenames:
            all_file.append(os.path.join(dir_path, name))
    return all_file


def is_or_not_file(path):
    """
    Method to determine if it is a file
    :param path: file or dir path
    :return:  True is File False is dir
    """
    return os.path.isfile(path)


def read_file(path, types):
    """

    :param path: fire path
    :param types: "r" or "rb"
    :return: list
    """
    with open(path, types, encoding="utf-8") as r:
        return r.readlines()


def remove_file(path):
    # checking if file exist or not
    if os.path.isfile(path):
        # os.remove() function to remove the file
        os.remove(path)
        # Printing the confirmation message of deletion
        print("File Deleted successfully")
    else:
        # Showing the message instead of Throwing an error
        print("File does not exist")


class ConvertImgToPdf:
    """将图片转为pdf的工具类"""

    def __init__(self, set_fixed_width=None, set_fixed_height=None):
        """set_fixed_width和set_fixed_height两个参数只能选一个"""
        self.set_fixed_width = set_fixed_width
        self.set_fixed_height = set_fixed_height
        # print("set_fixed_width:{}".format(self.set_fixed_width))
        # print("set_fixed_height:{}".format(self.set_fixed_height))

    def set_width_or_height(self, img):
        """判断是使用哪种方法,是固定宽度还是固定高度"""
        if self.set_fixed_width is not None and self.set_fixed_height is None:
            new_img = ResizeImg(img).fixed_width(self.set_fixed_width)  # 设置为固定宽度
        elif self.set_fixed_width is None and self.set_fixed_height is not None:
            new_img = ResizeImg(img).fixed_height(self.set_fixed_height)  # 设置为固定高度
        elif self.set_fixed_height is not None and self.set_fixed_width is not None:
            new_img = img
        else:
            new_img = img
        return new_img

    def convert_img_pdf(self, filepath, output_path):
        """
        转换图片为pdf格式
        Args:
            filepath (str): 文件路径
            output_path (str): 输出路径(包含文件名)。 XXX/XXX/name.pdf
        """
        output = Image.open(filepath)
        output = self.set_width_or_height(output)
        output.save(output_path, "pdf", save_all=True)

    def combine_imgs_pdf(self, folder_path, pdf_file_path):
        """
        合成文件夹下的所有图片为pdf
        Args:
            folder_path (str): 源文件夹
            pdf_file_path (str): 输出路径(包含文件名)。 XXX/XXX/name.pdf
        """
        files = os.listdir(folder_path)
        png_files = []
        sources = []
        for file in files:
            if 'png' in file or 'jpg' in file or "jpeg" in file:
                png_files.append(folder_path + file)
        png_files.sort()
        output = Image.open(png_files[0])
        output = self.set_width_or_height(output)  # 调整宽高
        png_files.pop(0)
        for file in png_files:
            png_file = Image.open(file)
            png_file = self.set_width_or_height(png_file)  # 调整宽高
            if png_file.mode == "RGB":
                png_file = png_file.convert("RGB")
            sources.append(png_file)
        output.save(pdf_file_path, "pdf", save_all=True, append_images=sources)


class ResizeImg:
    """调整图片大小的类"""

    def __init__(self, img):
        """初始化获取原始图片大小"""
        self.img = img
        self.width = img.width
        self.height = img.height

    def fixed_height(self, height):
        """设置固定高度"""
        ratio = self.height / height
        width = int(self.width / ratio)
        new_img = self.img.resize((width, height))
        return new_img

    def fixed_width(self, width):
        """设置固定宽度"""
        ratio = self.width / width
        height = int(self.height / ratio)
        new_img = self.img.resize((width, height))
        return new_img


def update_img_dpi(update_file_path, save_file_path, dpi_x=300, dpi_y=300):
    """
    修改图片的dpi
    :param update_file_path:  修改前图片地址，包含名称
    :param save_file_path:    修改后保存地址，包含名称
    :param dpi_x: dpi_x
    :param dpi_y: dpi_y
    :return:
    """
    output = Image.open(update_file_path)
    output.save(save_file_path, dpi=(dpi_x, dpi_y))


def get_sslcontext():
    """
    生成sslcontext，再去请求中传入ssl  |-->  ssl=sslcontext
    :exception
        aiohttp.client_exceptions.ClientConnectorError: Cannot connect to host www.mdnkids.com:443
        ssl:<ssl.SSLContext object at 0x1096634a8>
    Example:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50, loop=loop)) as session:
        r = await session.get('https://www.baidu.com', ssl=sslcontext)
    :return: sslcontext
    """
    FORCED_CIPHERS = (
        'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
        'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES'
    )
    sslcontext = ssl.create_default_context()
    sslcontext.options |= ssl.OP_NO_SSLv3
    sslcontext.options |= ssl.OP_NO_SSLv2
    sslcontext.options |= ssl.OP_NO_TLSv1_1
    sslcontext.options |= ssl.OP_NO_TLSv1_2
    sslcontext.options |= ssl.OP_NO_TLSv1_3
    sslcontext.set_ciphers(FORCED_CIPHERS)
    return sslcontext


def get_path_file_number(path):
    """获取指定路径下文件个数和文件夹个数path为Path对象 --> pathlib，不是str"""
    file_count = 0  # 文件个数
    dir_count = 0  # 文件夹个数
    files = os.listdir(path)
    # 输出所有文件名
    # print("所有文件名:")
    for file in files:
        # print(file)
        if is_or_not_file(path.joinpath(file)):
            file_count += 1
        if os.path.isdir(path.joinpath(file)):
            dir_count += 1
    count = {"file_count": file_count, "dir_count": dir_count}
    return count


def check_file_downloads(dir_path, txt_path, file_num, is_delete=False):
    """通过传入目录路径，获取目录下所有文件夹名称和文件夹下文件个数。检查实际下载跟需要下载的文件个数相差多少，再确定是否需要删除
       :param: dir_path  -->  Path("../datas/images/tag")
       :param: txt_path  -->  Path("../datas/tmp_txt")
       :param: file_num 相差文件个数
       :param: is_delete 是否需要删除文件夹相差比较大的文件夹
    """
    my_print("line")
    # 开始时间
    start_time = time.time()
    # 需要下载的总文件夹个数
    number_of_folders_to_download = count_lines(txt_path.joinpath("de_weight_tag_name.txt"))
    # 需要下载的总图片个数
    number_of_files_to_download = 0
    # 已下载封面数
    cover_download_count = 0
    all_file_count_list = read_file(txt_path.joinpath("de_weight_tag_name.txt"), "r")
    for tmp in all_file_count_list:
        number_of_files_to_download += int(tmp.split("|")[-3])
    my_print("需要下载的总文件夹个数:{}".format(number_of_folders_to_download), "blue")
    my_print("需要下载的总图片个数:{}".format(number_of_files_to_download), "green")
    file_count = 0  # 文件个数
    number_of_downloaded_folders = 0  # 已经下载文件夹个数
    number_of_downloaded_files = 0  # 已经下载文件夹个数
    file_count_list = get_all_files(dir_path)
    for tmp in file_count_list:
        if os.path.isfile(tmp):
            number_of_downloaded_files += 1
    dirs = os.listdir(dir_path)
    for dir_name in dirs:
        if os.path.isdir(dir_path.joinpath(dir_name)):
            number_of_downloaded_folders += 1
            # print(dir_name)
            page_count = dir_name.split("_")[-2].rstrip("P")
            # print(page_count)
            files = os.listdir(dir_path.joinpath(dir_name))
            dir_file_count = 0  # 文件个数
            for file in files:
                if os.path.isfile(dir_path.joinpath(dir_name, file)):
                    dir_file_count += 1
            # 如果相减大于传入的文件数，则表示文件还差多少个文件没有下载下来。需要重新下载一次。
            if int(page_count) - int(dir_file_count) >= file_num:
                print(page_count, dir_file_count, dir_name)
                if is_delete:
                    shutil.rmtree(dir_path.joinpath(dir_name))
                    print('\033[1;0;31m 文件{}未下载完全，超过{}个文件未下载，删除后重新下载！ \033[0m'
                          .format(dir_path.joinpath(dir_name), (int(page_count) - int(dir_file_count))))
            elif int(page_count) + 1 == int(dir_file_count):
                # my_print("文件  |-->  {}封面已下载完成。".format(dir_name))
                cover_download_count += 1
        elif os.path.isfile(dir_path.joinpath(dir_name)):
            file_count += 1
    my_print("{}个封面已下载完成。剩余{}个封面未下载。".format(cover_download_count,
                                             number_of_downloaded_folders - cover_download_count))
    my_print("已经下载文件夹个数:{}".format(number_of_downloaded_folders), "blue")
    my_print("已经下载图片个数:{}".format(number_of_downloaded_files), "green")
    if number_of_folders_to_download == number_of_downloaded_folders and \
            number_of_files_to_download == number_of_downloaded_files:
        my_print("所有图片已下载完成！！！", "pink")
    count = {"number_of_folders_to_download": number_of_folders_to_download,
             "number_of_files_to_download": number_of_files_to_download,
             "number_of_downloaded_folders": number_of_downloaded_folders,
             "number_of_downloaded_files": number_of_downloaded_files,
             "cover_download_count": cover_download_count}
    # 结束时间
    end_time = time.time()
    my_print("总用时{}秒。".format(round(end_time - start_time), 2))
    my_print(count, "yellow")
    my_print("line")
    return count


def set_str_color(print_str: object, color="white"):
    """
    设置打印字体颜色 前景色: 30（黑色）、31（红色）、32（绿色）、 33（黄色）、34（蓝色）、35（洋 红）、36（青色）、37（白色）
    :param print_str: 需要打印的对象
    :param color: 颜色英文名称
    :return: 修改后打印对象
    """
    if color == "black":
        tmp = '\033[1;0;30m {} \033[0m'.format(print_str)
    elif color == "red":
        tmp = '\033[1;0;31m {} \033[0m'.format(print_str)
    elif color == "green":
        tmp = '\033[1;0;32m {} \033[0m'.format(print_str)
    elif color == "yellow":
        tmp = '\033[1;0;33m {} \033[0m'.format(print_str)
    elif color == "blue":
        tmp = '\033[1;0;34m {} \033[0m'.format(print_str)
    elif color == "pink":
        tmp = '\033[1;0;35m {} \033[0m'.format(print_str)
    elif color == "cyan":
        tmp = '\033[1;0;36m {} \033[0m'.format(print_str)
    else:
        tmp = '\033[1;0;37m {} \033[0m'.format(print_str)
    return tmp


def my_print(print_str, color="white"):
    """
    自定义控制台打印
    :param print_str: 需打印字符串
    :param color: 打印颜色
    :return:
    """
    if print_str == "line":
        print(set_str_color("============================================================", "cyan"))
    else:
        print(set_str_color(print_str, color))


def get_new_list(txt_path: str, file_name: str, separator="|"):
    """
    根据本地文件获取列表文件，去除列表中分隔符号.
    :param txt_path:    # 本地文件路径，不包含文件名称
    :param file_name:   # 文件名
    :param separator:   # 分隔符
    :return: list
    """
    de_weight_url_list = read_file(Path(txt_path).joinpath(file_name), "r")
    new_de_weight_url_list = []
    for tmp in de_weight_url_list:
        tmp = tmp.split(separator)
        new_de_weight_url_list.append(tmp)
    return new_de_weight_url_list


def delete_cover_img(img_root_path, cover_name):
    """
    传入根路径，将路径下多个文件夹中的cover图片删除
    :param cover_name: 需要删除的封面名称
    :param img_root_path:    根路径
    :return:
    """
    cover_count = 0  # 删除封面数量
    dirs = os.listdir(img_root_path)
    for dir_ in dirs:
        files = os.listdir(Path(img_root_path).joinpath(dir_))
        for file in files:
            if file == cover_name:
                cover_path = str(Path(img_root_path).joinpath(dir_).joinpath(str(file)))
                my_print(cover_path, "pink")
                remove_file(cover_path)
                cover_count += 1
    my_print("一共删除了{}个封面。".format(cover_count), "red")


def imgs_to_pdf_more_folder(img_root_path, save_path, set_fixed_width=None, set_fixed_height=None):
    """
    传入根路径，将路径下多个文件夹中的图片单独保存为pdf文件
    :param save_path: 文件保存路径
    :param set_fixed_height: 设置固定高度
    :param set_fixed_width: 设置固定宽度
    :param img_root_path:    根路径
    :return:
    """
    # 开始时间
    start_time = time.time()
    dirs = os.listdir(img_root_path)
    combine_succeed_count = 0
    combine_failed_count = 0
    combine_exist_count = 0
    for dir_ in dirs:
        file_name = str(dir_) + ".pdf"
        save_name = save_path + file_name
        if not os.path.exists(save_name):
            my_print("开始合成pdf文件： |-->  {}".format(save_name), "yellow")
            # 直接保存到根目录
            try:
                ConvertImgToPdf(set_fixed_width, set_fixed_height).combine_imgs_pdf(img_root_path + dir_ + "\\", save_name)
                my_print("合成pdf文件成功： |-->  {}".format(save_name), "green")
                combine_succeed_count += 1
            except Exception as e:
                print(e)
                my_print("合成pdf文件失败！！！： |-->  {}".format(save_name), "red")
                combine_failed_count += 1
        else:
            my_print("pdf文件已存在，不需要合成！！！： |-->  {}".format(save_name), "red")
            combine_exist_count += 1

    # 结束时间
    end_time = time.time()
    my_print("总用时{}秒。成功{}个， 失败{}个，  已存在{}个！".format(
        round(end_time - start_time, 2), combine_succeed_count, combine_failed_count, combine_exist_count))
