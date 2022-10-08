#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 能跑就行，我就不按照什么标准啊什么的写了，
# 有些地方能省就省了
# 变量名也随便搞了
# 我还给你用中文注释了，我简直太贴心了啊
# 作者孟祥溪，mengxiangxibme^O^gmail.com
#
##################### 注意！#######################
# 该版本可用于Python 3，但未经严格测试，只作应急使用 #
##################################################

###版本号###
VERSION = '3.0'
###版本号###

import codecs  # 用于处理文本编码
import datetime
import os
import re  # 正则表达式
import sys

from utils import get_QJZ_date, change_date, initialize, convert_editor, get_editors_info


###################分割函数#####################

# doc string什么的就都不写了，这个函数的功能就是，
# 把搞下来的一坨长文件（种子文件）按照分区自动切分成N个文件，并且命名
def sepaFile(filename, termmode):
    # 首先判断种子文件是否为utf-8类型
    try:
        with codecs.open(filename+'.txt','rU','gbk') as testcode:
            testcode.read()
    except UnicodeDecodeError:
        print( u'检测到种子文件的编码方式可能是utf-8，现在进行编码转换。')
        oriFile = codecs.open(filename+'.txt','rU', 'utf8') # 原文件
        backup = codecs.open(filename+'utf8.txt','w','utf8') # 备份文件
        seedcontent = oriFile.readlines()
        for i in seedcontent: # 全部转写到备份文件
            backup.write(i)
        oriFile.close()
        print( u'已将原文档备份为'+filename+u'utf8.txt，存储在同一目录下。按任意键继续。')
        input('')
        backup.close()
        seedconvert = [] # 放置转码后的内容
        if termmode == 'w':
            seedconvert.append(seedcontent[0].encode('gbk'))
        else:
            seedconvert.append(seedcontent[0][1:].encode('gbk')) # 第一行涉及到文件头，单独处理
        for i in seedcontent[1:]: # 后面所有行
            seedconvert.append(i.encode('gbk'))
        oriFile = codecs.open(filename+'.txt','w', 'gbk') # 覆盖写入
        for i in seedconvert:
            oriFile.write(i.decode('gbk'))
        oriFile.close()

    # 正式分割
    oriFile = codecs.open(filename+'.txt','rU','gbk')
    # 这个done和后面的while是用来判断是不是到文件尾EOF
    done = 0
    grouplist = [] # 用来存放全部的分区
    voidlist = [] # 用于存放kong/void的分区
    while not done:
        sepabuff = '' # 变量名含义：分段的存储器
        linebuff = oriFile.readline() # 读一行，!请不要学我这样做，请使用readlines()
        # 这样读行保证了上一个分区结束后，下一个分区开始前可以有任意个空行
        if (linebuff !=''):
            # 判断是否以“发信人: ”开头，如果是，则是一个新帖子（新分区）
            if linebuff[:4] == u'发信人:':
                kong = 0 # 来判断是否为kong/void，默认为否
                linenum = 0 # 用来确定第二行的分区名称
                sepabuff += linebuff # 加在后面
                while (linebuff[:2] != '--'): # 用“--”来表示一个分区的结束
                    linebuff = oriFile.readline()
                    linenum += 1 # 光标下移
                    if (linenum == 1): # 第二行的位置找分区名称
                        groupchar = linebuff[6] # 分区名称存起来
                        if len(linebuff)>12 : # 如果文件名有"kong"/"void"，则一定超长
                            if linebuff[13] == 'k':
                                kong = 1
                            elif linebuff[13] == 'v':
                                kong = 1
                            elif linebuff[12] == 'k':
                                kong = 1
                            elif linebuff[12] == 'v':
                                kong = 1
                            # 以上支持“X@MMDD kong”或“X@MMDDkong”两类情况，kong/void两个关键字
                    sepabuff += linebuff # 存储分割的文件
                GrpFile = codecs.open(os.path.join(os.getcwd(),'QJZ@'+filename,groupchar+'@'+filename+'.grp'),'w','gbk')
                GrpFile.write(sepabuff) # 新建一个分区的文件，写进去
                GrpFile.close()
                print( groupchar+u"区内容分离完毕。")
                grouplist.append(groupchar) # 记录处理过的分区
                if kong == 1:
                    voidlist.append(groupchar) # 记录空分区
        else:
            done = -1 # 跳出循环
    oriFile.close()
    grouplist.sort() # 按顺序排好
    grouplistcontents = '' # 转写成字符串
    for i in grouplist:
        grouplistcontents += i[0]+u'、'
    print( u'以下'+str(len(grouplist)) +u'个分区处理完毕：')
    print( grouplistcontents[:-1]+u'。')
    nonvoidlist = list(set(grouplist) - set(voidlist)) # 获得非空分区
    nonvoidlist.sort() # 排序
    # 对于今日热点的处理：如果有今日热点，则调整到首位。
    if nonvoidlist[-1][0] == 'H' or nonvoidlist[-1][0] == 'h': # 判断今日热点的关键字
        nonvoidlist.insert(0, nonvoidlist[-1] ) # 最后一位插入第一位
        nonvoidlist.pop() # 删掉最后一位
    print( u'文件分割完成')
    return nonvoidlist


###################Body函数###################
# 用于映射不同分区的版面名的颜色代码
def colorTitle(brdtitle, grp):
    titledict ={
        'H': '31',
        'h': '31',
        '0': '36',
        '1': '35',
        '2': '34',
        '3': '33',
        '4': '32',
        '5': '31',
        '6': '36',
        '7': '35',
        '8': '34',
        '9': '33',
        'A': '32',
        'B': '31',
        'C': '36',
        'G': '35',
        }
    return u'  \u001B[1;'+str(titledict.get(grp))+u'm\u25B3 '+brdtitle.decode()

# 给出了各分区在QJZansisource.ans里的偏移量。
def fp2dict(num):
    fp2dict = {
        'H': 101,
        '0': 109,
        '1': 117,
        '2': 125,
        '3': 133,
        '4': 141,
        '5': 149,
        '6': 157,
        '7': 165,
        '8': 173,
        '9': 181,
        'A': 189,
        'B': 197,
        'C': 205,
        'G': 213,
        }
    return fp2dict.get(num)

#下面6个函数，用于映射每一行的偏移量。本来想用递归的方式，但是不会写。
def finalPlus2(grp, ansitemp, termmode):
    return ansitemp[fp2dict(grp)].strip()+'\r\n'

def finalPlus1(grp, ansitemp, termmode):
    return ansitemp[fp2dict(grp)-1].strip()+'\r\n'

def finalPlus0(grp, ansitemp, termmode):
    return ansitemp[fp2dict(grp)-2].strip()+'\r\n'

def finalMin1(grp, ansitemp):
    return ansitemp[fp2dict(grp)-3].strip()

def finalMin2(grp, ansitemp):
    return ansitemp[fp2dict(grp)-4].strip()

def finalMin3(grp, ansitemp):
    return ansitemp[fp2dict(grp)-5].strip()

# 大于4行的文字，倒数第四行以前，所有的色彩编码模式都是一样的。
def finalLeft(grp, ansitemp):
    return ansitemp[fp2dict(grp)-6].strip()

# 检查标点符号
def chkpunct(chkstr, grp):
    punctlist = [u'm', u'，', u'。', u'？', u'！', u'；', u'…'] # 所有可接受的标点符号
    punct = chkstr[-1:] # 行末的字符
    if punct not in punctlist: # 不在列表里
        print( u'####################')
        print( u'警告！请注意'+grp+u'区以下内容的行末标点是否出错：')
        print( chkstr[1:] )# 不包含预留的m或_
        print( u'按任意键继续。')
        print( u'####################')
        input('')

def chkboardsingle(boardname, grp, pubboarddict, priboarddict):
    boardname = boardname.decode()
    if pubboarddict.get(boardname,0) == 0:
        if priboarddict.get(boardname,0) == 0:
            print( u'####################')
            print( u'警告！请注意'+grp+u'区以下版名是否拼写正确：')
            print( boardname )
            print( u'在版名列表中未找到该版名。')
            print( u'按任意键继续。')
            print( u'####################')
            input('')
        elif priboarddict[boardname] == grp:
            print( u'####################')
            print( u'警告！请注意'+grp+u'区以下版面：')
            print( boardname )
            print( u'属于未登录不可见分区。')
            print( u'按任意键继续。')
            print( u'####################')
            input('')
        elif grp != 'H':
            print( u'####################')
            print( u'警告！请注意'+grp+u'区以下版面：')
            print( boardname )
            print( u'属于未登录不可见分区且属于'+priboarddict[boardname]+u'区。')
            print( u'按任意键继续。')
            print( u'####################')
            input('')
    elif pubboarddict[boardname] == grp or grp == 'H':
        return
    else:
        print( u'####################')
        print( u'警告！请注意'+grp+u'区以下版面：')
        print( boardname )
        print( u'其分区实际上应为'+pubboarddict[boardname]+u'区。')
        print( u'按任意键继续。')
        print( u'####################')
        input('')

def chkboardname(chkboardname, grp, pubboarddict, priboarddict):
    boardname = chkboardname.strip()
    numslash = 0
    for i in boardname:
        if re.match(r'[A-Za-z0-9/\_]+',chr(i)) == None:
            print( u'####################')
            print( u'警告！请注意'+grp+u'区以下版名是否含有特殊字符：')
            print( boardname )
            print( u'只能出现大小写英文字母、数字、下划线和“/”，不能出现空格等字符。')
            print( u'按任意键继续。')
            print( u'####################')
            input('')
        if i == '/':
            numslash += 1
    if numslash == 0:
        chkboardsingle(boardname, grp, pubboarddict, priboarddict)
    else:
        for i in range(0,numslash+1):
            chkboardsingle(boardname.split('/')[i], grp, pubboarddict, priboarddict)

# 从grp文件到body的内容
def getBody(grp, processFile, bodyfile, ansitemp, termmode, pubboarddict, priboarddict):
# grp：区；processFile：文件名；bodyfile：写入的文件；ansitemp：模板文件；termmode：Term类别
    bodysource = codecs.open(os.path.join(os.getcwd(), 'QJZ@'+processFile, grp+'@'+processFile+'.grp'), 'r', 'gbk')
    # 打开相应的grp文件
    bodyraw = bodysource.readlines() #全部放进来
    bodysource.close()
    bodylinenum = 3 # 设置初始偏移量，注意第一行读一个空行，方面下一步判断版面标题
    bodyutf = [] # 第二步暂存的容器
    # 每个分区全部正文读入bodyutf的容器
    while bodyraw[bodylinenum].strip() != '--': # 判断结尾
        bodyutf.append(bodyraw[bodylinenum].strip().encode('utf8'))
        bodylinenum += 1
    bodylinenum = len(bodyutf) # 方便倒着读取
    # 下面把文件最后所有的空行删掉
    while len(bodyutf[bodylinenum-1]) == 0: # 判断空行
        del bodyutf[bodylinenum-1]
        bodylinenum -= 1
    # 下面处理title
    bodylinenum = 0 # 行标
    nexttitle = 0 # 判断下一行是否为版面名（空行之后的一行是版面名）
    thistitle = 0 # 本行是否为版面名
    while bodylinenum < len(bodyutf):
        thistitle = nexttitle # 保存nexttitle的值
        if len(bodyutf[bodylinenum])== 0: # 执行判断：本行是否为空行？
            nexttitle = 1 # 空行的下一行是版名
        else:
            nexttitle = 0
        if thistitle == 1: # 处理这一行的版名
            chkboardname(bodyutf[bodylinenum], grp, pubboarddict, priboarddict)
            bodyutf[bodylinenum] = colorTitle(bodyutf[bodylinenum],grp) #调用函数
        elif bodyutf[bodylinenum].decode()[0:1] == '_': # 处理灰文字，标志符是“_”
            chkpunct(bodyutf[bodylinenum].decode('utf-8'), grp) # 检查标点
            bodyutf[bodylinenum] = u'     \u001B[0;37m'+bodyutf[bodylinenum].decode('utf8')[1:]
        else: # 不是版名、不是灰文字，则一定是正常文字
            bodyutf[bodylinenum] = u'     \u001B[0;1m'+ bodyutf[bodylinenum].decode('utf8')
            chkpunct(bodyutf[bodylinenum][10:], grp) # 检查标点，将m也传递进去，避免空白
        bodylinenum += 1
    # 规则：如果该分区只有一个版面，且该版面只有一行，则保留第一个空行，以保证分区图案完整
    # 不然直接从第一个版名开始，删去第一个空行
    if len(bodyutf) > 3:
        del bodyutf[0]
    bodyfinal = [] # 分区内容的第三个暂存容器
    for i in range(0,len(bodyutf)+4): # 初始化该容器，长度比bodyutf大4
        bodyfinal.append('')
    # 以倒序的方式逐步写入
    bodyfinal[len(bodyutf)+3] = u'\u001B[0;30m|\u001B[m\r\n'
    bodyfinal[len(bodyutf)+2] = finalPlus2(grp, ansitemp, termmode)
    bodyfinal[len(bodyutf)+1] = finalPlus1(grp, ansitemp, termmode)
    bodyfinal[len(bodyutf)] = finalPlus0(grp, ansitemp, termmode)
    bodyfinal[len(bodyutf)-1] = finalMin1(grp, ansitemp)+bodyutf[len(bodyutf)-1]+'\r\n'
    bodyfinal[len(bodyutf)-2] = finalMin2(grp, ansitemp)+bodyutf[len(bodyutf)-2]+'\r\n'
    bodyfinal[len(bodyutf)-3] = finalMin3(grp, ansitemp)+bodyutf[len(bodyutf)-3]+'\r\n'
    # 剩余的部分具有相同的结构
    if len(bodyutf)-3 > 0:
        for i in range(len(bodyutf)-4,-1,-1):
            bodyfinal[i] = finalLeft(grp, ansitemp)+bodyutf[i]+'\r\n'
    print(grp+u'区渲染完毕！')
    # 全部写入body文件
    for i in bodyfinal:
        bodyfile.write(i)

###################Foot函数###################
# 渲染主编/采编/美工/校对的ID颜色
def coloring(editorname, editorcolordict):
    if editorcolordict.get(editorname,0) == '1': # editorcolordict是主程序的global参数
        return u'\u001B[1;36m'+editorname+u'\u001B[m'
    elif editorcolordict.get(editorname,0) == '2':
        return u'\u001B[1;35m'+editorname+u'\u001B[m'
    elif editorcolordict.get(editorname,0) == '3':
        return u'\u001B[1;32m'+editorname+u'\u001B[m'
    else:
        print( u'居然有一个ID并不在列表中，极有可能是Editor.ans文件需要维护了。按任意键退出吧。')
        input('')
        sys.exit()


# 处理sepaFile()搞出来的分区文件（或者自动下载的文件），从中抽提采编姓名
def getFoot(foldername, filename, footaux):
    sourceFile = open(os.path.join(foldername, filename),'r',encoding='gbk') # 打开grp文件
    filebuff = sourceFile.readlines()
    editorname = filebuff[0].strip().split(' ')[1] # 采编名字在第一行的第二列
    grpname = filename[0] # 分区名从文件名读取
    footaux.write(grpname+' '+editorname+'\n') # 写入footaux文件
    sourceFile.close()

# 这个函数将采编列表均分成两行
def divide2lines(editorlist):
    errdict = {} # 记录每种断行方式的长度差绝对值
    # 评估所有可能性
    for i in range(1, len(editorlist)): # 遍历所有不同的断行可能性
        lenline1 = 0 # 第一行的长度
        lenline2 = 0 # 第二行的长度
        for j in range(0,i):
            lenline1 += len(editorlist[j])+1 #第一行所有元素的长度和（多一个空格）
        for k in range(i,len(editorlist)):
            lenline2 += len(editorlist[k])+1 #第二行所有元素的长度和（多一个空格）
        errdict[i] = abs(lenline2-lenline1) # 长度差（多的空格不影响）存入列表
    # 选择最佳方案
    sorterrlist = [] # 用于选择最优方案（长度差最小）
    for i in range(1,len(editorlist)): # 将字典的值转写入列表sorterrlist[]
        sorterrlist.append(errdict[i])
    sorterrlist.sort() # 对sorterrlist[]进行排序
    for i in range(1, len(editorlist)):
        if errdict[i] == sorterrlist[0]: # 找到第一个errdict[]中与最小值相对应的下标
            linebreakkey = i # 将下标存入linebreak
            break # 跳出
    # 准备输出
    editortwoline = [] # 返回值
    editortwoline1 = [] # 返回值第一行
    editortwoline2 = [] # 返回值第二行
    for i in range(0,len(editorlist)): # 遍历editorlist
        if i < linebreakkey: # linebreakkey之前的属于第一行
            editortwoline1.append(editorlist[i])
        else: # linebreakkey之后的属于第二行
            editortwoline2.append(editorlist[i])
    editortwoline.append(editortwoline1) # 分别连接两行
    editortwoline.append(editortwoline2)
    return editortwoline

# 这个函数将采编列表均分成三行
def divide3lines(editorlist):
    vardict = {} # 构建了类似方差的统计量，存放在这个字典里
    # 评估所有可能性
    for i in range(1, len(editorlist)-1): # 遍历不同断行可能性
        lenline1 = 0 # 第一行的长度
        lenline2 = 0 # 第二行的长度
        lenline3 = 0 # 第三行的长度
        for j in range(0,i):
            lenline1 += len(editorlist[j])+1 # 第一行的长度和
        editortwoline = divide2lines(editorlist[i:]) # 调用divide2lines()获取后两行长度
        for j in editortwoline[0]: # 获取倒数第二行长度
            lenline2 += len(j)+1
        for j in editortwoline[1]: # 获取最后一行长度
            lenline3 += len(j)+1
        # 计算统计量，该统计量是一阶中心矩的平方和
        var_ave = (lenline1+ lenline2+ lenline3)/3.0 # 计算平均值
        vari = (lenline1-var_ave)**2+(lenline1-var_ave)**2+(lenline1-var_ave)**2
        vardict[i] = vari # 记录每个统计量
    # 选择最佳方案
    sortvarlist = [] # 用于选择最优方案（统计量的值最小）
    for i in range(1, len(editorlist)-1):  # 将字典的值转写入列表sortvarlist[]
        sortvarlist.append(vardict[i])
    sortvarlist.sort() # 对sortvarlist[]进行排序
    for i in range(1, len(editorlist)-1):
        if vardict[i] == sortvarlist[0]:  # 找到第一个errdict[]中与最小值相对应的下标
            linebreakkey = i # 将下标存在linebreakkey
            break # 跳出
    editorthreeline = [] # 返回值
    editorthreeline1 = [] # 返回值第一行
    editorthreepara = [] # 调用后两行的函数参数
    for i in range(0,len(editorlist)): # 遍历editorlist
        if i < linebreakkey:  # linebreakkey之前的属于第一行
            editorthreeline1.append(editorlist[i])
        else: # linebreakkey之后的属于后两行
            editorthreepara.append(editorlist[i]) # 写入参数
    editorthreelineremain = divide2lines(editorthreepara) # 调用函数
    editorthreeline.append(editorthreeline1) # 写入第一行
    editorthreeline.append(editorthreelineremain[0]) # 写入第二行
    editorthreeline.append(editorthreelineremain[1]) # 写入第三行
    return editorthreeline

###################连接部分函数###################
# 该函数根据不同的Term查找所有的u'\u001B'，并替换成u'\u001B\u001B'，并处理换行符
def subststar(content, termmode):
    substresult = [] # 暂存的列表
    if termmode == 'w': # 对于Welly，换行符\n要删掉
        for i in content:
            substresult.append(i.strip().replace(u'\u001B',u'\u001B\u001B')+'\r')
    elif termmode == 'c': # 对于CTerm，只需双写u'\u001B'
        for i in content:
            substresult.append(i.replace(u'\u001B',u'\u001B\u001B')) # 利用字符串查找实现
    return substresult


#******************主程序******************
def main(QJZ_date=''):
    ###***###目录和文件管理###***###
    # cd到脚本所在目录
    #×#×#×##×#×#×#×#×#调试时可能需要注释掉#×#×#×##×#×#×#×#×#
    folder_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
    os.chdir(folder_path)
    #×#×#×##×#×#×#×#×#调试时可能需要注释掉#×#×#×##×#×#×#×#×#

    # 打开ANSI模板，并用列表管理
    ansisource = codecs.open(os.path.join('QJZansisource.ans'),'r','utf-8')
    ansitemp = ansisource.readlines() # 将模板文件的内容存储到ansitemp里面
    ansisource.close()

    # 从Editors.ans载入配置信息和排班表，建立字典
    chiefeddict = {} # 初始化主编排班的字典
    proofdict = {} # 初始化校对排班的字典
    termmode = '?'
    chiefedname = '?'
    if os.path.exists('setting'):
        with open('setting', 'r') as setting_file:
            termmode = setting_file.readline().strip()  # 第一行存储Term类型
            chiefedname = setting_file.readline().strip()  # 第二行存储默认主编
    with open('Editors.ans', 'r') as editor_file:
        for i in range(4):  # 1-4行存储周一到周四的主编和采编
            chiefeddict[i], proofdict[i] = editor_file.readline().strip().split(' ')
        # 第五行存储周六的主编和采编
        chiefeddict[5], proofdict[5] = editor_file.readline().strip().split(' ')

    # 从Editors.ans载入人员信息，建立字典
    # TODO(KakaHiguain): This part is in a mix, need to combine this with the last part.
    #  Also we should separate "Editors.ans" to three files: 1-2 lines: current chief editor,
    #  3-6 Schedule, 7-end Editor list.
    editorcolordict, editoraddlist, editordictupper = get_editors_info()

    # 打开版面列表
    if os.path.isfile('boardlist.csv'):
        boardnamefile = open('boardlist.csv','rU')
        boardnamebuffer = boardnamefile.readlines()
        for i in range(0, len(boardnamebuffer)):
            if boardnamebuffer[i].strip() == '-':
                boardnamecut = i
                break
        pubboarddict = {}
        for i in range(0,boardnamecut):
            pubboarddict[boardnamebuffer[i].strip().split(',')[0]] = boardnamebuffer[i].strip().split(',')[1]
        priboarddict = {}
        for i in range(boardnamecut+1, len(boardnamebuffer)):
            priboarddict[boardnamebuffer[i].strip().split(',')[0]] = boardnamebuffer[i].strip().split(',')[1]
    else:
        print(u'没有找到boardlist.csv，请运行QJZboardlist_x_x.py程序获取版名列表。')
        print(u'按任意键退出。')
        input('')
        sys.exit()

    ###***###初始化###***###
    # 初始化
    if termmode == '?':  # termmode为“?”，说明未经初始化
        termmode, chiefedname = initialize(editoraddlist, editordictupper)

    ###***###欢迎界面###***###
    print( u'欢迎使用QJZEditor '+VERSION+u'。请按照文档要求处理好采编内容，并保存在本脚本相同文件夹中。')
    print( u'请注意文件名的格式，应为“YYYYMMDD.txt。”')
    print( u'任何疑问，请联系作者，或在北大未名BBS起居注内部版发帖询问。')

    ###***###处理文件名，并分割文件###***###
    processFile = QJZ_date if QJZ_date else get_QJZ_date()

    # 检查相应文件是否存在
    while not os.path.isfile(processFile + '.txt'):
        print(u'不存在' + processFile + u'.txt，不是你把日期搞错了，就是你把文件名搞错了。下面重新输入。')
        processFile = None
        while not processFile:
            processFile = change_date()

    # 日期最终确定，再次更新周
    strQJZyear = processFile[0:4]
    strQJZmon = processFile[4:6]
    strQJZmday = processFile[6:8]
    QJZyear = int(processFile[0:4])
    QJZmon = int(processFile[4:6])
    QJZmday = int(processFile[6:8])
    QJZwday = datetime.date(QJZyear, QJZmon, QJZmday).weekday()# 更新周

    # 下一段儿就是看有没有QJZ@xxxxx这个文件夹，没有就给建了
    if os.path.isdir('QJZ@'+processFile):
        pass
    else:
        os.mkdir('QJZ@'+processFile)

    # 对文件进行分割
    bodylist = sepaFile(processFile, termmode) # 调用自定义函数分割文件，生成非空分区列表存于bodylist

    # 建立directory，用于存放全部分开的文件名
    currentdir = os.path.join('QJZ@'+processFile)
    directory = os.listdir(currentdir) # 获得当前文件列表

    # 如果后缀名不是.grp结尾的，则删掉该元素。
    indextodel = [] # 存放需要删掉元素的index
    for i in directory: # 遍历
        if i[-3:] != 'grp':
            indextodel.append(i)
    for i in indextodel: # 逐个删除
        directory.remove(i)
    directory.sort() # 将文件排序
    # 检查是否每个区都有采到
    for i in range(0,10): # 只检查0-9区
        if directory[i][:1] != str(i):
            print( u'z！你的'+str(i)+u'区呢？')
            input('Press enter to exit.')
            sys.exit()

    ###***###生成Header###***###
    # 这个字典用来翻译首行的色彩编码
    color_wday_dict = {
        0 : 31,
        1 : 32,
        2 : 33,
        3 : 35,
        5 : 36,
    }

    # 这个字典用来寻找从哪一行开始取出
    offset_wday_dict = {
        0: 1,
        1: 20,
        2: 39,
        3: 58,
        5: 77,
    }

    # 开始写入第一行的包含日期的内容
    colorcodewday = color_wday_dict[QJZwday] # 用于确定第一行的色彩代码，和后面保持一致
    # 下面打开源文件
    headerfile = codecs.open(os.path.join('QJZ@'+processFile, 'header'+processFile+'.txt'), 'w', 'utf-8')
    # 写下面各行
    headerfile.write(u'\u001B[0;30m|                           \u001B[')
    headerfile.write(str(colorcodewday)) # 色彩代码
    headerfile.write(u'm╰╂╯  ▂▂▂▂     \u001B[0;1m◇ ')
    headerfile.write(strQJZyear)
    headerfile.write(u'\u001B[0m年\u001B[1m')
    headerfile.write(strQJZmon)
    headerfile.write(u'\u001B[0m月\u001B[1m')
    headerfile.write(strQJZmday)
    headerfile.write(u'\u001B[0m日 \u001B[1m◇\r\n')
    # 写后面18行
    for i in range(0,18): # 到指定地点，读出后面18行
        headerfile.write(ansitemp[offset_wday_dict[QJZwday]+i])
    headerfile.close() # 该关的都关了

    print( u'已经把header存在'+processFile+u'文件夹的header'+processFile+u'.txt文件里面了。')
    print

    ###***###生成Body###***###
    # 新建一个存放body的文件，调用自定义函数写入body
    bodyfile = codecs.open(os.path.join('QJZ@'+processFile,'body'+processFile+'.txt'),'w','utf-8')
    for i in bodylist:
        getBody(i, processFile, bodyfile, ansitemp, termmode, pubboarddict, priboarddict) # 参数含义见自定义函数注释
    bodyfile.close()
    print( u'已经把body存在QJZ@'+processFile+u'文件夹的body'+processFile+u'.txt文件里面了。')
    print

    ###***###生成Footer###***###
    # 便于查错，这里还是保留了辅助文件
    footaux = open(os.path.join('QJZ@'+processFile,processFile+'foot.aux'),'w')
    for grpfilename in directory:
        getFoot(currentdir, grpfilename, footaux) # 调用自定义函数，写入各区采编名字
    footaux.close()

    # 载入分区采编信息
    footaux = open(os.path.join('QJZ@'+processFile,processFile+'foot.aux'),'r')
    editordict = {} # 采编列表，映射分区到采编
    for auxline in footaux:
        grpdict = auxline.strip().split(' ')[0] # 第一行是分区
        namedict = auxline.strip().split(' ')[1] # 第二行是采编
        editordict[grpdict]=namedict
    footaux.close()

    # 打印采编信息
    print( u'各区采编列表：')
    grplist_editordict = [] # 用一个傀儡列表实现顺序输出
    for i in editordict:
        grplist_editordict.append(i) # 加载editordict诸键值
    grplist_editordict.sort() # 排序
    for i in grplist_editordict:  # 依次输出
        print( u"%s区采编：" % i+editordict[i])
    print( u'是否更改？（y/N）')
    changeeditor = input('')
    changeeditor += '_' # 便于直接回车跳过

    # 更改采编
    while(changeeditor[0] == 'y' or changeeditor[0] == 'Y'):
        print( u'更改哪个区的采编？请输入数字或首字母。')
        changeeditorkey = input('')
        if changeeditorkey in ['a','b','c','g','h']: # 兼容非大写的分区名称
            changeeditorkey = changeeditorkey.upper() # 一律写成大写字母
        while editordict.get(changeeditorkey, '0')== '0':
            print(u'不存在这个区！重新输入！')
            changeeditorkey = input('')
            if changeeditorkey in ['a','b','c','g','h']:
                changeeditorkey = changeeditorkey.upper()
            continue
        print( str(changeeditorkey) + u'区当前的采编是'+ editordict[changeeditorkey])
        print( u'请输入更改后采编的ID（注意大小写）：')
        changeeditorvalue = input('')
        # ID纠错
        while(convert_editor(changeeditorvalue, editordictupper) == '0'):
            print( u'没有找到这个采编，请核对拼写或更新Editor.ans文件。')
            print( u'请输入更改后采编的ID：')
            changeeditorvalue = input('')
        editordict[changeeditorkey] = convert_editor(changeeditorvalue, editordictupper) # 实现采编的更改
        print( str(changeeditorkey) + u'区采编已更新为'+ editordict[changeeditorkey])
        print( u'是否继续更改其他分区的主编？（y/N）')
        changeeditor = input('')
        changeeditor += '_'
        # 完成修改后，重新打印并存入辅助文件
        if not(changeeditor[0] == 'y' or changeeditor[0] == 'Y'):
            footaux = open(os.path.join('QJZ@'+processFile,processFile+'foot.aux'),'w')
            print( u'最终的各区采编列表如下：')
            for i in grplist_editordict:
                print( u"%s区采编：" % i+editordict[i])
                footaux.write(i+' '+editordict[i]+"\n") # 存入辅助文件
            footaux.close()
            print( u'已更新分区列表。')

    # 对采编进行排序
    footaux = open(os.path.join('QJZ@'+processFile,processFile+'foot.aux'),'r')
    # 读入采编列表
    editorlist = []
    for i in footaux:
        editorlist.append(i.strip().split(' ')[1]) # 仅读入采编信息，不包括分区
    footaux.close()
    editorlist = list(set(editorlist)) # 利用集合数据类型实现删重复
    editorlist = sorted(editorlist,key = str.lower ) # 排序

    # 选择行数
    print(u'按两行排列采编的效果如下：')
    editor2line = divide2lines(editorlist) # 两行效果
    editorbuffer = '' # 用于存储待输出的内容
    for i in editor2line[0]:
        editorbuffer += i+' '
    print( editorbuffer )# 输出第一行
    editorbuffer = '' # 清空buffer
    for i in editor2line[1]: # 输出第一行
        editorbuffer += i+' '
    print( editorbuffer) # 输出第二行
    editorlinechoice = 2
    if len(editorlist) >= 3:
        print( u'按三行排列采编的效果如下：')
        editor3line = divide3lines(editorlist) # 两行效果
        editorbuffer = ''  # 清空buffer
        for i in editor3line[0]:
            editorbuffer += i+' '
        print( editorbuffer )# 输出第一行
        editorbuffer = '' # 清空buffer
        for i in editor3line[1]:
            editorbuffer += i+' '
        print( editorbuffer )# 输出第二行
        editorbuffer = '' # 清空buffer
        for i in editor3line[2]:
            editorbuffer += i+' '
        print( editorbuffer )# 输出第三行
        print( u'默认按两行排列，是否更改为按三行排列？（y/N）')
        changeto3lines = input('')
        changeto3lines += '_'
        if changeto3lines[0] == 'y' or changeto3lines[0] == 'Y':
            editorlinechoice = 3
        else:
            editorlinechoice = 2

    # 准备写入
    line1 = '' # 存放渲染后的第一行
    line2 = '' # 存放渲染后的第二行
    line3 = '' # 存放渲染后的第三行
    if editorlinechoice == 2:
        editorlines = divide2lines(editorlist) # 根据不同的情况调用函数
    elif editorlinechoice == 3:
        editorlines = divide3lines(editorlist) # 根据不同的情况调用函数

    for i in editorlines[0]: # 第一行
        line1 += coloring(i, editorcolordict)+' '
    for i in editorlines[1]: # 第二行
        line2 += coloring(i, editorcolordict)+' '
    if editorlinechoice == 3: # 如果有第三行，写入第三行，否则留空
        for i in editorlines[2]:
            line3 += coloring(i, editorcolordict)+' '

    # 处理主编预定义
    if len(chiefedname) < 3: # 如果没有预定义主编，则在此定义
        if len(chiefeddict[QJZwday]) < 3: # chiefeddict[QJZwday]不到3，说明排班主编未指定
            print( u'没有预设主编或排班表，请手动输入主编ID：') # 只能手动输入
            chiefedname = input('')
        else: # 没有预定义主编，但有排班主编
            print( u'没有预设主编，但排班表上的主编为'+chiefeddict[QJZwday]+u'。是否更改主编？(yes/No)')
            changechiefed = input('') # 允许更改
            changechiefed += '_'
            if changechiefed[0] == 'y' or changechiefed[0] == 'Y':
                print( u'请输入主编ID：')
                chiefedname = input('')
            else:
                chiefedname = chiefeddict[QJZwday]
    else: #如果有预定义的主编，则自动调用
        if chiefedname != chiefeddict[QJZwday] and len(chiefeddict[QJZwday])>3:
            # 如果也有排班，而且排班主编和预定义主编不同，则发出warning
            print( u'请注意，预设主编'+chiefedname+u'和排班表上所列主编'+chiefeddict[QJZwday]+u'不同。')
            print( u'默认将采用预设主编'+chiefedname+u'。是否更改主编？(yes/No)')
        else: # 只有预设主编，没有排班信息。
            print( u'预设主编为'+chiefedname+u'。是否更改主编？(yes/No)')
        # 两种情况下都有更改主编的可能
        changechiefed = input('')
        changechiefed += '_'
        if changechiefed[0] == 'y' or changechiefed[0] == 'Y':
            if len(chiefeddict[QJZwday])>3:
                print( u'是否将主编更改为排班表上的'+chiefeddict[QJZwday]+u'？(yes/No)')
                changetoroll = input('')
                changetoroll += '_'
                if changetoroll[0] == 'y' or changetoroll[0] == 'Y':
                    chiefedname = chiefeddict[QJZwday]
                else:
                    print( u'输入更改后主编的ID：')
                    chiefedname = input('')

    # 纠错
    while (convert_editor(chiefedname, editordictupper) == '0'):
        print( u'没有找到这个主编，请核对拼写或更新Editor.ans文件。')
        print( u'请重新输入主编ID：')
        chiefedname = input('')
    chiefname = editordictupper[chiefedname.upper()]
    print(u'现在的主编是'+chiefname+u'。')

    # 处理校对
    if len(proofdict[QJZwday])<3: # 先查排班表
        print( u'排班表上没有今天的校对，请输入手动输入校对ID：')
        proofname = input('')
    else:
        print( u'排班表上所列校对为'+proofdict[QJZwday]+u'。是否更改校对？(yes/No)')
        changeproof = input('')
        changeproof += '_'
        if changeproof[0] == 'y' or changeproof[0] == 'Y':
            print( u'输入更改后校对的ID：')
            proofname = input('')
            print( u'校对更改为'+chiefedname+u'。')
        else:
            proofname = proofdict[QJZwday]

    # 纠错
    while (convert_editor(proofname, editordictupper) == '0'):
        print( u'没有找到这个校对，请核对拼写或更新Editor.ans文件。')
        print( u'请重新输入校对ID：')
        proofname = input('')
    proofname = editordictupper[proofname.upper()]
    print(u'现在的校对是'+proofname+u'。')

    # 逐行写入文件
    footerfile = codecs.open(os.path.join('QJZ@'+processFile, 'footer'+processFile+'.txt'), 'w', 'utf-8')
    footerfile.write(ansitemp[223].strip()+coloring(chiefedname, editorcolordict)+'\r\n') # 第一行写入主编ID
    footerfile.write(ansitemp[224].strip()+line1+'\r\n') # 第二行写入采编第一行
    footerfile.write(ansitemp[225].strip()+'         '+line2+'\r\n') # 采编第二行
    footerfile.write(ansitemp[226].strip()+'         '+line3+'\r\n') # 采编第三行
    for i in range(227,230): # 连续写入
        footerfile.write(ansitemp[i])
    footerfile.write(ansitemp[230].strip()+coloring(proofname, editorcolordict)+'\r\n') # 校对ID
    footerfile.write(ansitemp[231])
    footerfile.write(ansitemp[232])
    footerfile.write(ansitemp[233]) # 连续写入
    footerfile.close()

    print( u'已经把footer存在QJZ@'+processFile+u'文件夹的footer'+processFile+u'.txt文件里面了。')
    print

    ###***###将各部分连接在一起，生成最终文件###***###
    # 如果是CTerm或Welly模式，则需要双写\u001B；如果是Welly模式，还需删除‘\n’
    if termmode == 'c' or termmode == 'w': # 进行双写
        currentdir = os.path.join('QJZ@'+processFile)
        txtdir = os.listdir(currentdir) # 获得当前文件列表
        indextodel = [] # 重置/复用列表，存放需要删掉元素的index
        for i in txtdir: # 遍历
            if i[-3:] != 'txt':
                indextodel.append(i)# 逐个删除
        for i in indextodel:
            txtdir.remove(i)
        for i in txtdir: # 每个txt分别处理
            substfile = codecs.open(os.path.join('QJZ@'+processFile, i), 'r', 'utf-8')
            substcontent = substfile.readlines() # 放在一个列表里
            substfile.close()
            substresult = subststar(substcontent, termmode) # 在列表中完成替换
            substfile = codecs.open(os.path.join('QJZ@'+processFile, i), 'w', 'utf-8')
            for j in substresult: # 写回去
                substfile.write(j)
            substfile.close()

    # 新建一个最终的文本文档
    QJZfinalfile = codecs.open(os.path.join('QJZ@'+processFile, 'QJZ@'+processFile+'.txt'), 'w', 'utf-8')
    # 写入header
    headerfile = codecs.open(os.path.join('QJZ@'+processFile, 'header'+processFile+'.txt'), 'r', 'utf-8')
    for i in headerfile:
        QJZfinalfile.write(i)
    headerfile.close()
    # 写入body
    bodyfile = codecs.open(os.path.join('QJZ@'+processFile,'body'+processFile+'.txt'),'r','utf-8')
    for i in bodyfile:
        QJZfinalfile.write(i)
    bodyfile.close()
    # 写入footer
    footerfile = codecs.open(os.path.join('QJZ@'+processFile, 'footer'+processFile+'.txt'), 'r', 'utf-8')
    for i in footerfile:
        QJZfinalfile.write(i)
    footerfile.close()
    QJZfinalfile.close()

    print(u'已经把连接好的最终文件存在QJZ@'+processFile+u'文件夹的QJZ@'+processFile+u'.txt文件里面了。\n')
    return proofname


if __name__ == '__main__':
    main()
