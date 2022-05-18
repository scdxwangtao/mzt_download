# -*- coding: UTF-8 -*-
"""
@Author: Aaron 
@E-mail: scdxwangtao@gmail.com
@ project name: mzt_download
@File: test_aiohttp.py
@CreateTime: 2022/5/7 20:35
"""
import aiohttp
import asyncio
from pathlib import Path


URL = [
    'https://cdn.pixabay.com/photo/2014/10/07/13/48/mountain-477832_960_720.jpg',
    'https://cdn.pixabay.com/photo/2013/07/18/10/56/railroad-163518_960_720.jpg',
    'https://cdn.pixabay.com/photo/2018/03/12/20/07/maldives-3220702_960_720.jpg',
    'https://cdn.pixabay.com/photo/2017/08/04/17/56/dolomites-2580866_960_720.jpg',
    'https://cdn.pixabay.com/photo/2016/06/20/03/15/pier-1467984_960_720.jpg',
    'https://cdn.pixabay.com/photo/2014/07/30/02/00/iceberg-404966_960_720.jpg',
    'https://cdn.pixabay.com/photo/2014/11/02/10/41/plane-513641_960_720.jpg',
    'https://cdn.pixabay.com/photo/2015/10/30/20/13/sea-1014710_960_720.jpg',
]


async def down_img(session, url, semaphore):
    """下载图片"""
    async with semaphore:
        name = url.split('/')[-1]  # 获得图片名字
        try:
            img = await session.get(url)
            # 触发到await就切换，等待get到数据
            content = await img.read()
            # 读取内容
            with open('../datas/down_img/'+str(name), 'wb') as f:
                # 写入至文件
                f.write(content)
                print(f'{name} 下载完成！')
            return str(url)
        except Exception as e:
            # await down_img(session, url, semaphore)
            print(e)
            # return str(url)


async def main(url_list):
    # 限制并发量为5
    semaphore = asyncio.Semaphore(5)
    # 建立会话session
    async with aiohttp.ClientSession() as session:
        # 建立所有任务
        tasks = [asyncio.create_task(down_img(session, img_url, semaphore)) for img_url in url_list]

        # # 触发await，等待任务完成
        # done, pending = await asyncio.wait(tasks)
        # all_results = [done_task.result() for done_task in done]
        # # 获取所有结果
        # print("ALL RESULT:"+str(all_results))

        all_results = await asyncio.gather(*tasks)
        print(all_results)

fp = Path("../datas/down_img")
if not fp.exists():
    fp.mkdir()
# asyncio.get_event_loop().run_until_complete(main(URL))    # python新版本弃用此方法。运行有警告。
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main(URL))

# asyncio.run(main(URL))
