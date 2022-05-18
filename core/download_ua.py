# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: download_ua.py
@CreateTime: 2022/5/13 17:04
"""
from pathlib import Path

import requests
import pandas as pd
from lxml import etree


def download_uas():
    """在线获取user—Agent保存到conf文件夹中。"""
    url = 'http://useragentstring.com/pages/useragentstring.php?typ=Browser'
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (compatible; ABrowse 0.4; Syllable)'
    }
    response = requests.get(url,
                            headers=header,
                            timeout=60
                            )
    tree = etree.HTML(response.text)
    browsers = tree.xpath('//ul/li/a/text()')
    browsers = [browser for browser in browsers if len(browser) > 80]       # 保存长度大于80的数据。

    # print(browsers)
    # print(len(browsers))

    df = pd.DataFrame({'id': range(1, len(browsers) + 1), 'ua': browsers})
    print(df)

    fp = Path('../conf/user_agents.csv')
    # 保存数据为csv文件
    df.to_csv(fp, index=False)

