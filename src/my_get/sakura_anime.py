# coding:utf-8

from concurrent.futures import ThreadPoolExecutor

import requests
import re
from m3u8_download import BaseM3u8Downloader


def get_main_m3u8_url(web_url):
    res = requests.get(web_url)
    res_content = res.content.decode('utf-8')
    m3u8_url = re.search(r'https://[a-zA-Z0-9%?&=_./\-]*m3u8', res_content)
    if not m3u8_url:
        print('没有获取到m3u8链接')
    # 这个主链接中包含多个不同清晰度的m3u8链接视频源
    return m3u8_url.group()
    

def get_video_url(main_m3u8_url):
    # 从第一个大的m3u8文件中找到子m3u8链接
    res = requests.get(main_m3u8_url)
    res_content = res.content.decode('utf-8')
    # return res_content
    # 匹配第一个m3u8链接，完成拼接  /20210831/Ny5lyotC/hls/index.m3u8
    host = re.search(r'https://[a-zA-Z0-9%?&=_.]*/', main_m3u8_url)
    path = re.search(r'/[a-zA-Z0-9%?&=_./]*m3u8', res_content)
    return host.group() + path.group()

def download(i:int):
    main_m3u8_url = get_main_m3u8_url(f'https://zgjmw.net/bofang/1944-0-{i}.html')
    # print(main_m3u8_url)
    video_url = get_video_url(main_m3u8_url)
    print(video_url)
    # 调用m3u8_downloader
    downloader = BaseM3u8Downloader()
    downloader.url = video_url
    downloader.video_path = f'I:/Videos/动漫/进击的巨人/'
    downloader.name = '进击的巨人%02d'%(i + 1)
    downloader.download()

if __name__ == '__main__':

    # 开启线程池执行
    with ThreadPoolExecutor(max_workers=10) as executor:
        task_list = [executor.submit(download, i) for i in range(0, 26)]
        for fu in futures.as_completed(task_list):
            print(fu.result(), fu)
