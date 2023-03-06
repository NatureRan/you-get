#coding:utf-8

from urllib import response
import requests,re,os,shutil
import asyncio
from ffmpy import FFmpeg

class BaseM3u8Downloader(object):
    def __init__(self):
        self.url = None
        self.__m3u8_url = None
        self.domain = None
        self.name = None
        self.__num = 0
        self.video_path = None
        self.__finish_num = 0
    
    def __create_dir(self):
        if not os.path.exists(f'src/my_get/{self.name}/'):
            os.mkdir(f'src/my_get/{self.name}/')
        if not os.path.exists(f'src/my_get/{self.name}/ts/'):
            os.mkdir(f'src/my_get/{self.name}/ts/')
        if not os.path.exists(self.video_path):
            os.mkdir(self.video_path)
    
    def __download_mp4(self):
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71"
        }
        response = requests.get(self.url,headers=headers,stream=True)
        chunk_size = 1024 # 单次请求最大值
        content_length = int(response.headers['content-length']) # 内容总体大小（字节）
        print(content_length, type(content_length))
        data_length = 0
        with open(f'{self.video_path}/{self.name}.mp4','wb') as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                data_length += len(data)
                print(f'{self.name} 正在下载 {int(data_length/1024)}KB / {int(content_length/1024)}KB 进度:{int(1.0 * data_length / content_length * 100)}%', end='\r')
        print(f'{self.name} 下载完成', end='\n')

    def __download_m3u8_url(self):
        response = requests.get(self.__m3u8_url)
        file = open(f'src/my_get/{self.name}/index.m3u8', 'w')
        file.write(response.content.decode('utf-8'))
        file.close()
        web_list=[]
        with open(f'src/my_get/{self.name}/index.m3u8','r') as files:
            lines_list=files.readlines()
            for https in lines_list:
                web=re.search("https://.+",https)
                if web:
                    web_list.append(web.group())
                    continue
                web=re.search("seg.+",https)
                if web:
                    web_list.append('https:.../'+web.group())
        files.close()
        self.__num = len(web_list)
        self.__finish_num = 0
        # 协程下载 （这边使用new_event_loop 而不是 get_event_loop，是因为event_loop只有主线程自带，外部使用多线程就无法get到event_loop了）
        # 如果外部没有开多线程，这个协程好像很慢。。。
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71"
        }
        tasks = [loop.create_task(self.__download_ts(url, num, headers)) for url,num in zip(web_list,range(1,self.__num+1))]
        loop.run_until_complete(asyncio.gather(*tasks))

    async def __download_ts(self, url, num, headers):
        i = 0
        while i<10:
            i+=1
            try:
                resp=requests.get(url,headers=headers)
                with open(f'src/my_get/{self.name}/ts/{num}.ts','wb') as codes:
                    codes.write(resp.content)
                    codes.close()
                    self.__finish_num += 1
                    print(f'{self.name} 下载进度:{self.__finish_num}/{self.__num}', end='\r')
                break
            except Exception as e:
                print(f'{self.name} {num}.ts 下载失败')
                print(e)

    def __change(self):
        """
        由于这个m3u8文件比较特殊，里面头部信息为png，我们要将它修改成ts
        :param num: 这个就是总共的ts数
        :return: 返回修改过后的ts文件
        """
        print(f'{self.name} 正在修改文件内容')
        current_path = os.getcwd()
        current_path = current_path.replace('\\', '/')
        for i in range(1, self.__num+1):#num+1
            with open(f"src/my_get/{self.name}/ts/{i}.ts","rb") as in_file:
                data = in_file.read()
                out_file = open(f"src/my_get/{self.name}/ts/{i}.ts","wb")
                out_file.write(data)
                out_file.seek(0x00)
                out_file.write(b'\xff\xff\xff\xff')
                out_file.flush()
                out_file.close()
            in_file.close()
            print(f'{self.name} 内容修改进度:{i}/{self.__num}', end = '\r')
        print(f'{self.name} 内容修改完成')

    def __together(self):
        """
        合并outlib列表中的所有ts文件
        :param name: 爬取视频的名字
        :return: 返回一个MP4文件
        """
        # 整合文件索引
        current_path = os.getcwd()
        current_path = current_path.replace('\\', '/')
        video_file_name = f'{self.video_path}/{self.name}.mp4'
        # 判断文件是否存在
        if os.path.exists(video_file_name):
            print(f'{video_file_name} 已经存在')
            return
        with open(f"src/my_get/{self.name}/filelist.txt","w", encoding='utf-8') as file:
            file.write("\n")
            for i in range(1, self.__num+1):#num+1
                file.write(f"file  '{current_path}/src/my_get/{self.name}/ts/{i}.ts'\n")
        file.close()
        
        ff=FFmpeg(
            inputs={
                f"src/my_get/{self.name}/filelist.txt":"-f concat -safe 0"
            },
            outputs={
                video_file_name:"-c copy"
            }
        )
        # print(ff.cmd)
        try:
            ff.run()
        except Exception as e:
            print(f'{video_file_name} 合成失败')
            print(e)

    def __del_temp(self):
        shutil.rmtree(f'src/my_get/{self.name}/', True)

    def download(self):
        assert self.video_path
        assert self.url
        assert self.name
        self.__create_dir()
        if 'm3u8' in self.url:
            # m3u8下载
            self.__m3u8_url = self.url
            self.__download_m3u8_url()
            self.__change()
            self.__together()
        elif 'mp4' in self.url:
            # mp4下载
            self.__download_mp4()
        
        # 删除中间文件，只留最后的视频
        self.__del_temp()
        
if __name__ == '__main__':
    downloader = BaseM3u8Downloader()
    downloader.url = 'https://v1.cdtlas.com/20210831/Ny5lyotC/hls/index.m3u8'
    downloader.name = '进击的巨人01'
    downloader.video_path = 'I:/Videos/动漫/进击的巨人/'
    downloader.download()