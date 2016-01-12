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
import time
import datetime

# 下面这个函数把周几换成中文
def get_week_day(date):
  week_day_dict = {
    0 : u'星期一',
    1 : u'星期二',
    2 : u'星期三',
    3 : u'星期四',
    4 : u'星期五',
    5 : u'星期六',
    6 : u'星期日',
  }
  day = date.weekday()
  return week_day_dict[day]

localtime = time.localtime(time.time()) # 获取当地时间
# 用下面几个变量存放年月日周
QJZyear = localtime.tm_year
QJZmon = localtime.tm_mon
QJZmday = localtime.tm_mday
QJZwday = datetime.datetime.now().weekday()
# 打印出来默认的日期
print u"今天是"+str(QJZyear)+u"年"+str(QJZmon)+\
      u"月"+str(QJZmday)+u"日，"+get_week_day(datetime.datetime.now())\
      +u"\n要更改日期么？(yes/No):"
changedate = raw_input('') # 判断是否更改日期
changedate += '_' # 允许用户直接按Enter键跳过
# 手动更新年月日
if changedate[0] == 'y' or changedate[0] == 'Y':
  print u'输入新的年份：'
  QJZyear = int(raw_input(''))
  print u'输入新的月份：'
  QJZmon = int(raw_input(''))
  print u'输入新的日期：'
  QJZmday = int(raw_input(''))
  # 更新周
  QJZwday = datetime.date(QJZyear, QJZmon, QJZmday).weekday()
  # 打印出更新的日期
  print u"修改后的日期是：\n"+str(QJZyear)+u"年"+str(QJZmon)+\
      u"月"+str(QJZmday)+u"日，"+get_week_day(datetime.date(QJZyear, QJZmon, QJZmday))\
      +u"\n再看一眼没错吧？错了就重来，别让校对捉住了。"
# 判断是否为周五或周日
if QJZwday == 4 or QJZwday == 6:
  print u'你是Z么，周五和周日停刊啊！按任意键再来一遍，记得检查好问题。'
  raw_input()
  sys.exit() # 退出程序

#################

# 将年月日转化成文本
strQJZyear = unicode(QJZyear)
if QJZmon < 10:
  strQJZmon = '0'+unicode(QJZmon)
else:
  strQJZmon = unicode(QJZmon)
if QJZmday < 10:
  strQJZmday = '0'+unicode(QJZmday)
else:
  strQJZmday = unicode(QJZmday)

os.chdir(os.path.dirname(sys.argv[0])) # 转到当前文件夹（For Mac）
filename = strQJZyear+strQJZmon+strQJZmday
# 下一段儿就是看有没有Output@xxxxx这个文件夹，没有就给建了
if os.path.isdir('Output@'+filename):
  pass
else:
  os.mkdir('Output@'+filename)
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
# 下面打开源文件ansisource.ans和目标文件
headerfile = codecs.open(os.path.join('Output@'+filename, 'header'+filename+'.txt'), 'w', 'utf-8')
ansisource = codecs.open('QJZansisource.ans','r','utf-8')
# 开始一步步写入第一行
colorcodewday = color_wday_dict[QJZwday]
headerfile.write(u'\u001B[0;30m|                           \u001B[')
headerfile.write(unicode(colorcodewday))
headerfile.write(u'm╰╂╯  ▂▂▂▂     \u001B[1;37m◇ \u001B[30m')
headerfile.write(strQJZyear)
headerfile.write(u'\u001B[0m年\u001B[1;30m')
headerfile.write(strQJZmon)
headerfile.write(u'\u001B[0m月\u001B[1;30m')
headerfile.write(strQJZmday)
headerfile.write(u'\u001B[0m日 \u001B[1m◇\n')
# 写后面18行
for i in range(0,offset_wday_dict[QJZwday]): # 先扔掉前面若干行
  ansisource.readline()
for i in range(1,19): # 到指定地点，读出后面18行
  headerfile.write(ansisource.readline())
ansisource.close()
headerfile.close() # 该关的都关了

# 重新打开一次
headerfile = codecs.open(os.path.join('Output@'+filename, 'header'+filename+'.txt'), 'r', 'utf-8')
print u'现在已经给你弄好了，就是下面的样子：'
print headerfile.read() # 输出一遍
headerfile.close()
print u'如果上面是乱码，请不要惊慌，有的编译器可尝试直接复制粘贴。'
print u'已经把头部存在Output@'+filename+u'文件夹的header'+filename+u'.txt文件里面了。'
print u'现在，按任意键退出吧。'
raw_input()
sys.exit()
