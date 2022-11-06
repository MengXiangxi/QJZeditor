#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
from BDWM import BDWM
import getpass
import os
import base64
import sys

#admin0-9 ABCG https://bbs.pku.edu.cn/v2/board.php?bid={xxx}
boardlists_dic = {"BBShelp":"0 0"}
boards_bid={
    "0":"621",  #0区目录
    "1":"664",  #1区目录
    "2":"671",  #2区目录
    "3":"673",  #3区目录
    "4":"674",  #4区目录
    "5":"675",  #5区目录
    "6":"678",  #6区目录
    "7":"679",  #7区目录
    "8":"680",  #8区目录
    "9":"681",  #9区目录
    "A":"682",  #A区目录
    "B":"683",  #B区目录
    "C":"685",  #C区目录
    "D":"686",  #D区目录
    "F":"687",  #F区目录
    "G":"688"   #G区目录
}

def get_decoded_password(file):
    """read password and decode it"""
    if not os.path.exists(file):
        return None
    with open(file, 'r') as f:
        encoded_password = f.read()
    return base64.b64decode(encoded_password.encode()).decode()

def write_encoded_password(password, file):
    """encode password and write it"""
    encoded_password = base64.b64encode(password.encode()).decode()
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, 'w') as f:
        f.write(encoded_password)

# 根据request权限读取版面目录，并标记mark  0-游客可见 1-仅登录可见
def get_board_mark(boardlists_dic,request,mark):
    for board in boards_bid.keys():
        url = "https://bbs.pku.edu.cn/v2/board.php?bid="+boards_bid[board]
        #response = bdwm._session.get(url)
        response = request.get(url)
        soup = BeautifulSoup(response.text, features="lxml")
        
        # class = left左边添加收藏夹/ class = upper 列表
        boardlists_engname = soup.select('.set .upper .eng-name') 
        for j in range(0,len(boardlists_engname)):
            boardlists_dic[boardlists_engname[j].text] = "{} {}".format(board,mark)

def main():
    #pyinstaller 打包时获取正确路径 支持py+exe
    base_path = ""
    if getattr(sys, 'frozen', False):  # 判断sys中是否存在frozen变量,
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)

    #支持读取token
    password_file = os.path.join(base_path, '.token', 'token')
    password = get_decoded_password(password_file)
    if not password:
        password = getpass.getpass("请输入WMWZ的密码(不会显示)：")
        # Store encoded password in a file, to avoid inputting password every time.
        write_encoded_password(password, password_file)

    #登录WMWZ并建立session
    try:
        bdwm = BDWM('WMWZ',password)
    except BDWM.RequestError as e:
        # If failing to login, remove wrong password file.
        os.remove(password_file)
        raise e

    print("获取所有版面中...")        
    get_board_mark(boardlists_dic,bdwm._session,"1")
    print("已获取所有版面，更新游客可见版面中...")
    guest = requests
    get_board_mark(boardlists_dic,guest,"0")
    print("已更新所有版面，写入文件中...")

    # 写入文件 格式 版名 分区 是否登录可见（0-游客可见 1-仅登录可见）
    with open(os.path.join(base_path,'boardlist.ans'), 'w+', encoding='utf8') as f:
        for board in boardlists_dic:
            f.write(("{} {}\n").format(board,boardlists_dic[board]))
            print(board)

if __name__ == "__main__":
    main()
