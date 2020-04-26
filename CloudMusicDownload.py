# Author:akai
# Blog:http://www.akaina.top/

import os
import time
import re
import urllib.request as urllibreq
import win32clipboard as wc
import win32con
import pickle  # 序列化


class CloudMusicDownloader(object):
    '''
    网易云音乐下载器，用户只需在歌曲列表中右键复制歌曲链接即可将歌曲下载到本地中，
    在本地音乐中匹配音乐可以将下载的歌曲同步到网易云音乐软件中。
    '''

    def __init__(self):
        self.useInfo()
        self.setConfig()
        self.CONFIG = self.getConfig()

    def useInfo(self):
        print('欢迎您使用网易云音乐下载器\n'
              '使用说明：在歌曲列表中右键复制歌曲链接即可实现下载。\n'
              '侵权说明：本程序仅用于学习交流。')

    def setConfig(self):
        if not os.path.exists('config.txt'):
            print("配置音乐保存路径，此路径为网易云音乐保存的路径。\n"
                  "例如安装在F盘则路径应该为：F:/CloudMusic")
        else:
            # 配置文件
            with open("config.txt", 'rb') as f:
                CONFIG = pickle.load(f, encoding="utf8")
            if "CloudMusic" in CONFIG['SAVEPATH']:
                return
            print("配置音乐保存路径不正确，此路径为网易云音乐保存的路径。\n"
                  "例如安装在F盘则路径应该为：F:/CloudMusic")
        CONFIG = {
            "SAVEPATH": input("输入保存音乐的地址:").replace("\\", "/")
        }
        with open("config.txt", 'wb') as f:
            pickle.dump(CONFIG, f)
        return

    def getConfig(self):
        # 载入配置文件
        with open("config.txt", 'rb') as f:
            CONFIG = pickle.load(f, encoding="utf8")
        return CONFIG

    def getClipboardText(self):
        # 获取剪切板最新内容
        try:
            wc.OpenClipboard()
            t = wc.GetClipboardData(win32con.CF_TEXT)
            wc.CloseClipboard()
            text = t.decode('utf-8')
            return text
        except UnicodeDecodeError:
            return

    def getMusicId(self, link):
        # 获取歌曲ID
        pattern = '(.*)music.163.com(.*)id=(\d+)&(.*)'
        try:
            result = re.search(pattern, link)
            if result != None:
                MusicId = result.group(3)
                return MusicId
        except:
            return None

    def download(self, MusicId):
        # 下载网易云音乐歌曲
        songurl = r"http://music.163.com/song/media/outer/url?id={}.mp3".format(MusicId)
        filename = MusicId + '.mp3'
        try:
            startTime = time.time()
            urllibreq.urlretrieve(songurl, self.CONFIG["SAVEPATH"] + '/' + filename)
            endTime = time.time()
            costTime = (endTime - startTime) * 1000
            print(f'{filename}歌曲下载成功,耗时{round(costTime, 2)}ms,保存位置为 {self.CONFIG["SAVEPATH"]}。')
        except Exception as e:
            print('下载失败，请重试。\n'f"失败可能原因：{e}")

    def run(self):
        print('程序运行中...')
        tempLink = None
        while True:
            time.sleep(1)
            # 1、获取歌曲链接
            link = self.getClipboardText()
            # 1.1、检测链接是否有变更，无变更则不进行操作。
            if tempLink == link and link != None:
                continue
            tempLink = link
            MusicId = self.getMusicId(link)
            # 2、获取歌曲id
            # 2.1、判断是否是网易云歌曲链接
            if MusicId == None:
                continue
            # 3、下载歌曲
            for root, dir, files in os.walk(self.CONFIG["SAVEPATH"]):
                filename = f"{MusicId}.mp3"
                if filename in files:
                    print(f"{filename}歌曲已存在，无须下载。")
                else:
                    self.download(MusicId)
                break


if __name__ == '__main__':
    cmd = CloudMusicDownloader()
    cmd.run()