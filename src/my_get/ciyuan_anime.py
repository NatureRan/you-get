#coding:utf-8

from m3u8_download import BaseM3u8Downloader
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from concurrent.futures import ThreadPoolExecutor
from concurrent import futures
import time,json,re,threading,asyncio

class CiYuanAnimeDownloader(BaseM3u8Downloader):

    def __init__(self):
        super().__init__()

caps = DesiredCapabilities.CHROME
caps['loggingPrefs'] = {
    'browser':'ALL',
    'performance':'ALL',
}
caps['perfLoggingPrefs'] = {
    'enableNetwork' : True,
    'enablePage' : False,
    'enableTimeline' : False
}
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"')
chrome_options.add_experimental_option('w3c', False) # 设置这个属性可以使用driver.get_log()方法 不然报错


async def find_video_url(url):
    print(f'开始抓取url:{url}')
    driver.get(url)
    time.sleep(3)
    text = driver.find_element_by_xpath('//a[@class="module-play-list-link active"]/span').text
    for log_type in driver.log_types:
        request_logs = driver.get_log(log_type)
        for log in request_logs:
            # 遍历log所有字段，匹配出https开头，m3u8结束的字符
            m3u8 = re.search(r'https://[a-zA-Z0-9%?&=_./\-]*m3u8', json.dumps(log))
            if m3u8:
                print(f'{text} 抓取到m3u8链接 {m3u8.group()}')
                return text,m3u8.group()
            mp4 = re.search(r'https://[a-zA-Z0-9%?&=_./\-]*mp4', json.dumps(log))
            if mp4:
                print(f'{text} 抓取到mp4链接 {mp4.group()}')
                return text,mp4.group()
    return '', ''

def crawler_video_urls(name, index, size):
    print(f'开始搜索片名:{name}')
    driver.get(f'http://www.cycdm01.top/search.html?wd={name}')
    try:
        driver.find_element_by_xpath('//a[@class="play-btn-o"]').click()
        elements = driver.find_elements_by_xpath('//div[@class="module-list sort-list tab-list his-tab-list active"]//a[@class="module-play-list-link"]')
    except Exception as e:
        elements = None
    if elements:
        print(f'搜索到资源 {name} 共{len(elements)}集')
    else:
        print(f'没有搜索到资源 {name}')
        return
    urls = []
    video_urls = {}
    for e in elements:
        urls.append(e.get_attribute('href'))
    # 判断index是否超出总集数
    if index > len(elements):
        print('设置的集数超出总集数')
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(find_video_url(urls[i])) for i in range(index - 1, min(index + size - 1, len(elements)))]
    loop.run_until_complete(asyncio.gather(*tasks))
    # 获取协程的返回结果
    for task in tasks:
        text, video_url = task.result()
        if not text:
            continue
        video_urls[text] = video_url
    return video_urls

def download(name, key, url):
    ciYuanAnimeDownloader = CiYuanAnimeDownloader()
    ciYuanAnimeDownloader.video_path = f'I:/Videos/动漫/{name}/'
    ciYuanAnimeDownloader.url = url
    ciYuanAnimeDownloader.name = name + '-' + key
    ciYuanAnimeDownloader.download()




if __name__ == '__main__':
    name = '机动战士高达 水星的魔女'
    index = 6 # 从第几集开始 （最小1）
    size = 1 # 一次下载的集数
    # 初始化chromeDriver
    driver = webdriver.Chrome(desired_capabilities=caps, chrome_options=chrome_options)
    try:
        video_urls = crawler_video_urls(name, index, size)
    except Exception as e:
        pass
    finally:
        driver.quit()
    if not video_urls:
        print('没有抓取到视频链接')
        exit()

    # 开启线程池执行
    with ThreadPoolExecutor(max_workers=10) as executor:
        task_list = [executor.submit(download, name, key, video_urls.get(key)) for key in video_urls.keys()]
        for fu in futures.as_completed(task_list):
            print(fu.result(), fu)
