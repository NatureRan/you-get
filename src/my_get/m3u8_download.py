#coding:utf-8

import requests,re,os,shutil
from ffmpy import FFmpeg

def download_m3u8(url:str):
    response = requests.get(url)
    file = open('src/my_get/index.m3u8', 'w')
    file.write(response.content.decode('utf-8'))
    file.close()
    web_list=[]
    with open(f'src/my_get/index.m3u8','r') as files:
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
    headers={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71"
    }
    if not os.path.exists('src/my_get/ts/'):
        os.mkdir('src/my_get/ts/')
    for url,num in zip(web_list,range(1,len(web_list)+1)):
        i = 0
        while i<10:
            i+=1
            try:
                resp=requests.get(url,headers=headers)
                with open(f'src/my_get/ts/{num}.ts','wb') as codes:
                    codes.write(resp.content)
                    codes.close()
                    print(f'{num}.ts 下载完成')
                break
            except Exception as e:
                print(f'{num}.ts 下载失败')
                print(e)
    return len(web_list)

def change(num):
    """
    由于这个m3u8文件比较特殊，里面头部信息为png，我们要将它修改成ts
    :param num: 这个就是总共的ts数
    :return: 返回修改过后的ts文件
    """
    print("正在加载....")
    if not os.path.exists('src/my_get/ts/'):
        os.mkdir('src/my_get/ts/')
    if not os.path.exists('src/my_get/ts_out/'):
        os.mkdir('src/my_get/ts_out/')
    current_path = os.getcwd()
    with open("src/my_get/filelist.txt","w") as file:
        file.write("\n")
        for i in range(1,num+1):#num+1
            file.write(f"file  '{current_path}\\src\\my_get\\ts_out\\{i}.ts'\n")
            with open(f"src/my_get/ts/{str(i)}.ts","rb") as infile:
                out_ts = f"src/my_get/ts_out/{str(i)}.ts"
                outfile = open(out_ts, "wb")
                data = infile.read()
                outfile.write(data)
                outfile.seek(0x00)
                outfile.write(b'\xff\xff\xff\xff')
                outfile.flush()
                outfile.close()
            infile.close()
    file.close()

def together(name):
    """
    合并outlib列表中的所有ts文件
    :param name: 爬取视频的名字
    :return: 返回一个MP4文件
    """
    ff=FFmpeg(
        inputs={
            "src/my_get/filelist.txt":"-f concat -safe 0"
        },
        outputs={
            f"{name}.mp4":"-c copy"
        }
    )
    # print(ff.cmd)
    ff.run()

def del_temp():
    shutil.rmtree('src/my_get/ts/', True)
    shutil.rmtree('src/my_get/ts_out/', True)
    os.remove('src/my_get/index.m3u8')
    os.remove('src/my_get/filelist.txt')

if __name__ == '__main__':
    num = download_m3u8('')
    change(num)
    together('')
    # 删除中间文件，只留最后的视频
    del_temp()
