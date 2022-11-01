#coding:utf-8

from m3u8_download import BaseM3u8Downloader
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time,json,re

class CiYuanAnimeDownloader(BaseM3u8Downloader):

    def __init__(self):
        super().__init__()

def crawler_m3u8(name):
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
    driver = webdriver.Chrome(desired_capabilities=caps, chrome_options=chrome_options)
    driver.get(f'http://www.cycdm01.top/search.html?wd={name}')
    driver.find_element_by_xpath('//a[@class="play-btn-o"]').click()
    eles = driver.find_elements_by_xpath('//div[@class="module-list sort-list tab-list his-tab-list active"]//a[@class="module-play-list-link"]')
    urls = []
    m3u8_urls = {}
    for ele in eles:
        urls.append(ele.get_attribute('href'))
    for url in urls:
        driver.get(url)
        time.sleep(3)
        text = driver.find_element_by_xpath('//a[@class="module-play-list-link active"]/span').text
        for log_type in driver.log_types:
            request_logs = driver.get_log(log_type)
            for log in request_logs:
                # 遍历log所有字段，匹配出https开头，m3u8结束的字符
                m3u8 = re.search(r'https://[a-zA-Z0-9%?&=./]*m3u8', json.dumps(log))
                if m3u8:
                    m3u8_urls[text] = m3u8.group()
    driver.quit()
    return m3u8_urls

if __name__ == '__main__':
    name = '边缘行者'
    m3u8_urls = crawler_m3u8(name)
    ciYuanAnimeDownloader = CiYuanAnimeDownloader()
    ciYuanAnimeDownloader.video_path = f'/Users/nature/Movies/{name}/'
    for key in m3u8_urls.keys():
        ciYuanAnimeDownloader.m3u8_url = m3u8_urls.get(key)
        ciYuanAnimeDownloader.name = name + '-' + key
        ciYuanAnimeDownloader.m3u8_download()