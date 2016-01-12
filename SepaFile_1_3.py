#!/usr/bin/env python
# coding=utf-8
# 能跑就行，我就不按照什么标准啊什么的写了，
# 有些地方能省就省了
# 变量名也随便搞了
# 我还给你用中文注释了，我简直太贴心了啊
# 作者孟祥溪，mengxiangxibme_AT_g^m^a^i^l.com

import os
import codecs
import sys

# doc string什么的就都不写了，这个函数的功能就是，
# 把搞下来的一坨长文件按照分区自动切分成N个文件，并且命名
def sepaFile(filename):
    # 下一段儿就是看有没有GrpFile@xxxxx这个文件夹，没有就给建了
    if os.path.isdir('GrpFile@'+filename):
        pass
    else:
        os.mkdir('GrpFile@'+filename)
    # 打开这一坨长文件
    oriFile = open(filename+'.txt','r')
    # 这个done和后面的while是用来判断是不是到文件尾EOF
    done = 0
    grouplist = []
    while not done:
        sepabuff = '' # 变量名含义：分段的存储器
        linebuff = oriFile.readline() # 读一行，!请不要学我这样做，请使用readlines()
        if (linebuff !=''):
            # 判断是否以“发信人: ”开头，如果是，则是一个新帖子（新分区）
            if linebuff[:8].decode('gbk') == u'发信人: ':
                linenum = 0 # 用来确定第二行的分区名称
                sepabuff += linebuff # 加在后面
                while (linebuff[:2] != '--'): # 用“--”来表示一个分区的结束
                    linebuff = oriFile.readline()
                    linenum += 1
                    if (linenum == 1): # 第二行的位置找分区名称
                        groupchar = linebuff[8:9] # 分区名称存起来
                    sepabuff += linebuff
                GrpFile = open(os.path.join('GrpFile@'+filename,groupchar+'@'+filename+'.grp'),'w')
                GrpFile.write(sepabuff) # 新建一个分区的文件，写进去
                GrpFile.close()
                print groupchar+u"区内容分离完毕。"
                grouplist.append(groupchar) # 记录处理过的分区
        else:
            done = -1 # 跳出循环
    oriFile.close()
    grouplist.sort() # 按顺序排好
    grouplistcontents = '' # 转写成字符串
    for i in grouplist:
        grouplistcontents += i+u'、'
    print u'以下'+str(len(grouplist)) +u'个分区处理完毕：'
    print grouplistcontents[:-1]+u'。'


separationfile = raw_input(u'请输入文件名:\n'.encode('gbk'))
#separationfile = '20151219'
#print 'GrpFile@'+separationfile
os.chdir(os.path.dirname(sys.argv[0]))
sepaFile(separationfile)
raw_input(u'按任意键结束。\n'.encode('gbk'))
