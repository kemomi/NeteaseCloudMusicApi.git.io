#!/usr/bin/python
import os
import time
import sys

from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
import requests
from pydub import AudioSegment
import json

# 不需要动
base_url = "http://39.98.194.220:3000"


# None的转为‘’
def xstr(s):
    return '' if s is None else str(s)


# 获取歌曲url
def getSongsUrl(songIds, cookies, songsMap):
    url = base_url + "/song/url?id=" + songIds + "&&timestamp=" + str(int(round(time.time() * 1000)))
    r = requests.get(url, cookies=cookies)
    json = r.json()
    songsUrlData = json.get("data")
    for song in songsUrlData:
        song_url = song.get("url")
        songsMap[song.get("id")] = {"url": song_url}


# 获取歌曲的 名称，歌手，专辑，专辑封面
def getSongsInfo(songsMap, songIds):
    url = base_url + "/song/detail?ids=" + songIds + "&&timestamp=" + str(int(round(time.time() * 1000)))
    r = requests.get(url)
    json = r.json()
    songsData = json.get("songs")
    for song in songsData:
        name = song['name']
        artist = song.get("ar")[0].get("name")
        album = song.get("al").get("name")
        pic = song.get("al").get("picUrl")
        # 取出值 然后再赋值
        songTmp = songsMap[song.get("id")]
        songTmp['name'] = name
        songTmp['artist'] = artist
        songTmp['album'] = album
        songTmp['pic'] = pic
        songsMap[song.get("id")] = songTmp


# 设置mp3信息
def setMp3Info(count, mp3file, info):
    try:
        songFile = ID3(mp3file)
        songFile['APIC'] = APIC(  # 插入封面
            encoding=3,
            mime='image/jpeg',
            type=3,
            desc=u'Cover',
            data=info['pic']
        )
        songFile['TIT2'] = TIT2(  # 插入歌名
            encoding=3,
            text=info['title']
        )
        songFile['TPE1'] = TPE1(  # 插入第一演奏家、歌手、等
            encoding=3,
            text=info['artist']
        )
        songFile['TALB'] = TALB(  # 插入专辑名
            encoding=3,
            text=info['album']
        )
        songFile.save()
    except Exception:
        print(mp3file + "--发生异常 -- " + count)
    else:
        print(mp3file + "--处理完成 -- " + count)


# 下载歌曲并且设置参数
def downloadItem(count, url, name, pic, artist, album, savePath):
    if url is None or name is None:
        print(name, '该资源不存在')
        return
    name = name.replace('/', '／').replace('\\', '＼')
    # 读取MP3资源
    res = requests.get(url, stream=True)
    fileName, ext = os.path.splitext(url)
    # 获取文件地址
    file_path = os.path.join(savePath, name + ext)
    mp3_file_path = os.path.join(savePath, name + ".mp3")
    if os.path.exists(mp3_file_path):
        print(name + " 已存在 -- " + count)
        return

    # 打开本地文件夹路径file_path，以二进制流方式写入，保存到本地
    with open(file_path, 'wb') as fd:
        fd.write(res.content)
        fd.flush()
    # 不是mp3 将其转换成mp3
    if ext != '.mp3':
        audio = AudioSegment.from_file(file_path)
        audio.export(mp3_file_path, format="mp3")
        # 删除其他格式源文件
        os.remove(file_path)
        file_path = mp3_file_path

    # 图片流文件
    r = requests.get(pic)
    info = {'pic': r.content,
            'title': name,
            'artist': artist,
            'album': album}
    setMp3Info(count, file_path, info)


# 文件夹不存在，则创建文件夹
def initFolder(savePath):
    folder = os.path.exists(savePath)
    if not folder:
        os.makedirs(savePath)


# 循环下载
def download(savePath, songsMap):
    initFolder(savePath)
    count = 0
    os.chdir(savePath)
    for (key, song) in songsMap.items():
        url = song.get("url")
        name = song.get("name")
        pic = song.get("pic")
        artist = song.get("artist")
        album = song.get("album")
        # 下载文件并且设置
        count = count + 1
        downloadItem(str(count), url, name, pic, artist, album, savePath)


# 获取歌单中歌曲ids
def getSongsId(playId, cookies, param_map):
    try:
        url = base_url + "/playlist/detail?id=" + playId + "&&timestamp=" + str(int(round(time.time() * 1000)))
        r = requests.get(url, cookies=cookies)
        playList = r.json().get("playlist")
        trackIds = playList.get("trackIds")
        print("专辑封面：" + playList.get("coverImgUrl"))
        albumName = playList.get("name")
        # 放入变量中
        param_map['albumName'] = albumName
        print("专辑名称：" + albumName)
        print("专辑描述：" + xstr(playList.get("description")))
        print("歌曲数量：" + str(len(trackIds)))
        list_new = map(lambda x: str(x.get("id")), trackIds)
        if len(trackIds) == 0 or not list_new:
            print("该歌单为空！歌单名称：" + albumName)
            sys.exit()
        else:
            return ",".join(list_new)
    except AttributeError:
        print("歌单不存在～～")
        sys.exit()


# 获取配置
def getConfig():
    with open('config.json', 'r') as f:
        data = json.load(f)

    return (data.get("base_path"), data.get("playId"), data.get("token"))


if __name__ == '__main__':
    # 配置信息
    (base_path, playId, token) = getConfig()
    for param in (base_path, playId, token):
        assert '<' not in param, '请设置参数：' + param
    base_path += "/" if base_path[-1] != "/" else ""

    param_map = {}
    cookies = {}
    cookies["MUSIC_U"] = token
    songIds = getSongsId(playId, cookies, param_map)
    songsMap = {}
    getSongsUrl(songIds, cookies, songsMap)
    # 获取歌曲信息(专辑封面)
    getSongsInfo(songsMap, songIds)
    # 下载文件并且设置参数
    savePath = base_path + param_map["albumName"]
    print("开始下载")
    download(savePath, songsMap)
    print("下载完成！")
