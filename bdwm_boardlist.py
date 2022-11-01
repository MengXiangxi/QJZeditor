#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
from BDWM import BDWM
import getpass

#admin0-9 ABCG https://bbs.pku.edu.cn/v2/board.php?bid={xxx}
boards_bid=[
    "621",  #0区目录
    "664",  #1区目录
    "671",  #2区目录
    "673",  #3区目录
    "674",  #4区目录
    "675",  #5区目录
    "678",  #6区目录
    "679",  #7区目录
    "680",  #8区目录
    "681",  #9区目录
    "682",  #A区目录
    "683",  #B区目录
    "685",  #C区目录
    "686",  #D区目录
    "687",  #F区目录
    "688"   #G区目录
    ]

boardlists_dic = {"BBShelp":"0 0"}

userid =input("请输入BBS帐号(推荐使用WMMZ)：")
password = getpass.getpass("请输入密码(不会显示)：")
try:
    bdwm = BDWM('WMWZ', password)
except BDWM.RequestError as e:
    # If failing to login, remove wrong password file.
    print("password error")
    raise e

## 使用高权限帐号获取所有版面目录
for i in range(0,len(boards_bid)):
    url = "https://bbs.pku.edu.cn/v2/board.php?bid="+boards_bid[i]
    response = bdwm._session.get(url)
    soup = BeautifulSoup(response.text, features="lxml")
    
    partition = ''
    if(i < 10):
        partition = chr(48+i)
    elif(i < 14):
        partition = chr(55+i)
    else:
        partition = chr(56+i)

    # class = left左边添加收藏夹/ class = upper 列表
    boardlists_engname = soup.select('.set .upper .eng-name') 
    for j in range(0,len(boardlists_engname)):
        boardlists_dic[boardlists_engname[j].text] = "{} 1".format(partition)

    print("正在添加{}区目录".format(partition))

## 使用游客帐号获取所有不登陆可见版面目录,并更新字典
for i in range(0,len(boards_bid)):
    url = "https://bbs.pku.edu.cn/v2/board.php?bid="+boards_bid[i]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="lxml")
    
    partition = ''
    if(i < 10):
        partition = chr(48+i)
    elif(i < 14):
        partition = chr(55+i)
    else:
        partition = chr(56+i)

    # class = left左边添加收藏夹/ class = upper 列表
    boardlists_engname = soup.select('.set .upper .eng-name') 
    for j in range(0,len(boardlists_engname)):
        boardlists_dic[boardlists_engname[j].text] ="{} 0".format(partition)
        
    print("{}区已更新完毕".format(partition))

# 格式 版名 分区 是否登录可见（0-游客可见 1-仅登录可见）
with open('boardlist.ans', 'w+', encoding='utf8') as f:
    for board in boardlists_dic:
        f.write(("{} {}\n").format(board,boardlists_dic[board]))
