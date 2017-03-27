#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 能跑就行，我就不按照什么标准啊什么的写了，
# 有些地方能省就省了
# 变量名也随便搞了
# 我还给你用中文注释了，我简直太贴心了啊
# 作者孟祥溪，mengxiangxibme^O^gmail.com

###版本号###
ver = '0.1'
###版本号###

import os
import codecs # 用于处理文本编码
import sys
import urllib2 # 用于获取Gist API
import json # 用于解析json


#******************主程序******************
###***###目录和文件管理###***###
# cd到脚本所在目录
#×#×#×##×#×#×#×#×#调试时可能需要注释掉#×#×#×##×#×#×#×#×#
folder_path = os.path.split(os.path.realpath(__file__))[0]
os.chdir(folder_path)
#×#×#×##×#×#×#×#×#调试时可能需要注释掉#×#×#×##×#×#×#×#×#

# 判断是否存在Editors.ans，若否则创建一个，并写入空白信息。
# 若存在，则保存前两行自定义信息，并备份。
if os.path.isfile('Editors.ans'):
    editorsource = open(os.path.join('Editors.ans'),'r')
    editors = editorsource.readlines()
    line1 = editors[0] # 保存Term习惯
    line2 = editors[1] # 保存主编ID
    editorsource.close()
    editortarget = open(os.path.join('Editors_backup.ans'),'w') # 备份
    for i in editors:
        editortarget.write(i)
    editortarget.close()
    print(u'已将Editors.ans备份为Editors_backup.ans。按任意键继续。')
    raw_input('')
else:
    editorlist = open(os.path.join('Editors.ans'),'w')
    editorlist.write('?\r\n?\r\n') # 写入前两行
    editorlist.close()
    print(u'不存在Editors.ans。已经新建了一个。')

print(u'通讯中...')

url = "https://api.github.com/gists/7537c01cffd86b175653c9989bc7daed"
# 用GET方式从Gist上获取内容
try:
    content = urllib2.urlopen(url).read()
except:
    print(u'网络连接错误，按任意键退出。')
    raw_input('')
    sys.exit()
data = json.loads(content) # 对response的json格式字符串进行解析
print(u'下载成功，数据版本：%s。' %data['updated_at'])

# 写入Editors.ans
editortarget = open(os.path.join('Editors.ans'),'w')
editortarget.write(line1)
editortarget.write(line2) # 写入前两行
fileBody = data['files']['Editors.ans']['content'] # 此为Gist的内容
editortarget.write(fileBody) # 写入抓取的内容
editortarget.close()

# 在备份文件中记录当前版本
backupfile = open(os.path.join('Editors_backup.ans'),'a')
backupfile.write(data['updated_at']+' 0')
backupfile.close()

print(u'已将Editor.ans更新至%s的版本。按任意键退出。'%data['updated_at'])
raw_input('')



