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

grpdict ={
    '[本科]' : 'C',
    '[本站]' : '0',
    '[地区]' : '2',
    '[电脑]' : '4',
    '[感性]' : '7',
    '[高校]' : '2',
    '[机构]' : 'B',
    '[俱乐]' : 'G',
    '[群体]' : 'A',
    '[社会]' : '8',
    '[社团]' : 'A',
    '[双修]' : 'C',
    '[硕博]' : 'C',
    '[谈天]' : '7',
    '[体育]' : '9',
    '[网络]' : '4',
    '[文化]' : '5',
    '[系统]' : '4',
    '[校内]' : '1',
    '[校务]' : 'F',
    '[新版]' : 'N',
    '[新闻]' : '8',
    '[信息]' : '8',
    '[休闲]' : '6',
    '[学科]' : '3',
    '[研讨]' : '3',
    '[艺术]' : '5',
    '[游戏]' : '6',
    '[娱乐]' : '6',
    '[院系]' : '1',
    '[组织]' : 'B',
    }

insideboardlist = {
    'manager' : '0',
    'BMTseven' : '0',
    'Admin3_Office' : '3',
    'DevTeam' : '0',
    'watertest' : '0',
    'NewDevGroup' : '0',
    'Downstairs' : '0',
    'TshirtsVote' : '0',
    'ArbClub' : '0',
    'Architects' : '0',
    'BMTone' : '0',
    'BMTnine' : '0',
    'Admin1_Office' : '1',
    'ASCII_club' : '0',
    'sandbox' : '0',
    'Admin8_Office' : '8',
    'minuxtest' : '0',
    'TeamANNI' : '0',
    'Mailbox' : '0',
    'Admin5_Office' : '5',
    'BMTsix' : '0',
    'RulesRevision' : '0',
    'AdminG_Talk' : 'G',
    'Admin6_Office' : '6',
    'Jail' : '0',
    'Cultivation' : '5',
    'AdminG_Office' : 'G',
    'DailyRoutine' : '0',
    'TuanGouOffice' : '8',
    'AdminG_Test' : 'G',
    'AnniMB' : '0',
    'WWWStudio' : '0',
    'Admin7_Office' : '7',
    'BBShelp' : '0',
    'BMTfive' : '0',
    'BMTtwo' : '0',
    'BMTraining' : '0',
    'WMQJZ' : '0',
    'colorzone' : '0',
    'Admin6_Closed' : '6',
    'CreativeStudio' : '0',
    'ITMarketOffice' : '4',
    'BMTeight' : '0',
    'WMWiki' : '4',
    'BMTestT' : '0',
    'Editors' : '0',
    'Reconstruction' : '0',
    'BMTthree' : '0',
    'MarketCenter' : '8',
    'Admin4_Office' : '4',
    'BoardClub' : '0',
    'BMTfour' : '0',
    'SomeBoard' : '8',
    'Admin8_Club' : '8',
    'JudgeCommittee' : '5',
    'AcademicOffice' : '3',
    'AdminABC_Office' : 'A',
    }


#******************主程序******************
###***###目录和文件管理###***###
# cd到脚本所在目录
#×#×#×##×#×#×#×#×#调试时可能需要注释掉#×#×#×##×#×#×#×#×#
#folder_path = os.path.split(os.path.realpath(__file__))[0]
#os.chdir(folder_path)
#×#×#×##×#×#×#×#×#调试时可能需要注释掉#×#×#×##×#×#×#×#×#
if os.path.isfile('boardlist.csv'):
    boardsource = codecs.open(os.path.join('boardlist.csv'),'rU','gbk')
    boards = boardsource.readlines()
    boardsource.close()
    boardstarget = codecs.open(os.path.join('boardlist_backup.csv'),'w','gbk')
    for i in boards:
        boardstarget.write(i)
    boardstarget.close()
    print(u'已将boardlist.csv备份为boardlist_backup.csv。按任意键继续。')
    raw_input('')
else:
    boardlist = codecs.open(os.path.join('boardlist.csv'),'w','gbk')
    boardlist.close()
    print(u'不存在boardlist.csv。已经新建了一个。')

boardnamedict = {}

print(u'通讯中...')

try:
    content = urllib2.urlopen('http://www.bdwm.net/bbs/bbsall.php').readlines()
except:
    print(u'网络连接错误，按任意键退出。')
    raw_input('')
    sys.exit()
print(u'已下载'+unicode(len(content)/10-6)+u'条版面信息。')
for i in range(28,len(content)-37,10):
    boardnamedict[content[i].split('=')[3].split('"')[0]] = content[i+2][16:22]

for i in boardnamedict:
    boardval = boardnamedict[i].strip().decode('gbk').encode('utf')
    if grpdict.get(boardval, 0) == 0:
        print(u'程序遇到文本识别问题，无法运行，请联系调试。')
        raw_input('')
    else:
        boardnamedict[i] = grpdict[boardval]

boardlist = open(os.path.join('boardlist.csv'),'w')
for i in boardnamedict:
    boardlist.write(i+','+boardnamedict[i]+'\n')
print(u'已写入'+unicode(len(boardnamedict))+u'条公开版面记录。')
boardlist.write('-')
for i in insideboardlist:
    boardlist.write('\n'+i+','+insideboardlist[i])
boardlist.close()
print(u'已写入'+unicode(len(insideboardlist))+u'条内部版面记录。')
print(u'按任意键退出。')
raw_input('')
