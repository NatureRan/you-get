#coding:utf-8

import requests,re,os,shutil
import asyncio
from ffmpy import FFmpeg

class BaseM3u8Downloader(object):
    def __init__(self):
        self.m3u8_url = None
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

    def __download_m3u8_url(self):
        response = requests.get(self.m3u8_url)
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
        # 协程下载
        asyncio.run(self.___download_web_list(web_list))
        
        
    async def ___download_web_list(self, web_list):
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71"
        }
        tasks = [asyncio.create_task(self.__download_ts(url, num, headers)) for url,num in zip(web_list,range(1,self.__num+1))]
        await asyncio.gather(*tasks)

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
        with open(f"src/my_get/{self.name}/filelist.txt","w") as file:
            file.write("\n")
            for i in range(1, self.__num+1):#num+1
                file.write(f"file  '{current_path}/src/my_get/{self.name}/ts/{i}.ts'\n")
        file.close()
        
        ff=FFmpeg(
            inputs={
                f"src/my_get/{self.name}/filelist.txt":"-f concat -safe 0"
            },
            outputs={
                f"{self.video_path}/{self.name}.mp4":"-c copy"
            }
        )
        # print(ff.cmd)
        ff.run()

    def __del_temp(self):
        shutil.rmtree(f'src/my_get/{self.name}/', True)

    def m3u8_download(self):
        assert self.video_path
        assert self.m3u8_url
        assert self.name
        self.__finish_num = 0
        self.__create_dir()
        self.__download_m3u8_url()
        self.__change()
        self.__together()
        # 删除中间文件，只留最后的视频
        self.__del_temp()
