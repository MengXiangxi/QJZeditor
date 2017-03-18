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
import urllib2 # 用于获取网页代码


#******************主程序******************
###***###目录和文件管理###***###
# cd到脚本所在目录
#×#×#×##×#×#×#×#×#调试时可能需要注释掉#×#×#×##×#×#×#×#×#
#folder_path = os.path.split(os.path.realpath(__file__))[0]
#os.chdir(folder_path)
#×#×#×##×#×#×#×#×#调试时可能需要注释掉#×#×#×##×#×#×#×#×#
if os.path.isfile('Editors.ans'):
    editorsource = codecs.open(os.path.join('Editors.ans'),'rU','gbk')
    editors = editorsource.readlines()
    editorsource.close()
    editortarget = codecs.open(os.path.join('Editors_backup.ans'),'w','gbk')
    for i in editors:
        editortarget.write(i)
    editortarget.close()
    print(u'已将Editors.ans备份为Editors_backup.ans。按任意键继续。')
    raw_input('')
else:
    editorlist = codecs.open(os.path.join('Editors.ans'),'w','gbk')
    editorlist.write('?\r\n?\r\n0 0\r\n0 0\r\n0 0\r\n0 0\r\n0 0')
    editorlist.close()
    print(u'不存在Editors.ans。已经新建了一个。')

print(u'通讯中...')

url ="http://www.bdwm.net/bbs/bbsanc.php?path=/groups/GROUP_0/PersonalCorpus/P/peiyangium/D639F7551/A4D5F6896" 
try:
    content = urllib2.urlopen(url).readlines()
except:
    print(u'网络连接错误，按任意键退出。')
    raw_input('')
    sys.exit()
print(u'下载成功，数据版本：%s。' %content[48].strip())

contentstrip = []
for i in range(49,len(content)-23):
    contentstrip.append(content[i])
editorsource = codecs.open(os.path.join('Editors.ans'),'rU','gbk')
line1 = editorsource.readline()
line2 = editorsource.readline()
editorsource.close()
editortarget = codecs.open(os.path.join('Editors.ans'),'w','gbk')
editortarget.write(line1)
editortarget.write(line2)
for i in contentstrip:
    editortarget.write(i.strip()+'\r\n')

backupfile = codecs.open(os.path.join('Editors_backup.ans'),'a','gbk')
backupfile.write(content[48].strip()+' 0')
backupfile.close()

print(u'已将Editor.ans更新至%s的版本。按任意键退出。'%content[48].strip())
raw_input('')

editortarget.close()

