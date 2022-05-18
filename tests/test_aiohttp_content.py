# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: test_aiohttp_content.py
@CreateTime: 2022/5/9 17:33
"""
import asyncio

import aiohttp


async def main():
    """边下边保存"""
    async with aiohttp.ClientSession() as session:
        url = 'https://download.jetbrains.com/python/pycharm-professional-2022.1.exe'
        async with session.post(url) as resp:
            with open('pycharm.exe', 'wb') as fd:
                # iter_chunked() 设置每次保存文件内容大小，单位bytes
                async for chunk in resp.content.iter_chunked(1024):
                    fd.write(chunk)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
