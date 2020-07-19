#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 21:37:13 2020

@author: KakaHiguain@BDWM
"""

import datetime

SEPARATE_BAR = "======================"


def get_content_from_raw_string(content_string):
    parts = content_string.split('\u001B[')
    template = '{{"type":"ansi","bold":{},"underline":{},"fore_color":{},' \
               '"back_color":{},"content":"{}"}}'
    bold, underline, fore_color, back_color = 'false', 'false', 9, 9
    res = []
    for part in parts:
        pos = part.find('m')
        if pos > -1:
            font_codes = part[:pos].split(';')
            if len(font_codes) == 1 and font_codes[0] == '':
                font_codes[0] = '0'
            for code in font_codes:
                code = int(code)
                if code in range(30, 40):
                    fore_color = code - 30 if code <= 37 else 9
                elif code in range(40, 50):
                    back_color = code - 40 if code <= 47 else 9
                elif code == 1:
                    bold = 'true'
                elif code == 4:
                    underline = 'true'
                elif code == 0:
                    bold, underline, fore_color, back_color = 'false', 'false', 9, 9
                else:
                    pass
        content = part[pos + 1:].replace("\\", '\\\\') \
                                .replace('\"', '\\\"') \
                                .replace('\n', '\\n')
        res.append(template.format(bold, underline, fore_color, back_color, content))

    return '[{}]'.format(','.join(res)).replace('\x1b', '')


def yes_or_no_prompt(prompt_string, func, **argv):
    ans = input('{}(yes/No)'.format(prompt_string))
    if ans and ans[0] in ['y', 'Y']:
        func(**argv)
    else:
        print('跳过~')


def wrap_separate_bar(s):
    return '{0}{1}{0}'.format(SEPARATE_BAR, s)


def format_string(s, format_code):
    return '\033[{}m{}\033[0m'.format(format_code, s)


def bold_string(s):
    return format_string(s, '1')


def bold_red(s):
    return format_string(s, '1;31')


def bold_green(s):
    return format_string(s, '1;32')


def bold_yellow(s):
    return format_string(s, '1;33')


def get_weekday(date):
    """Turn the date to Chinese weekday"""
    week_day_dict = {
        0: u'星期一',
        1: u'星期二',
        2: u'星期三',
        3: u'星期四',
        4: u'星期五',
        5: u'星期六',
        6: u'星期日',
    }
    day = date.weekday()
    return week_day_dict[day]


def change_date():
    print(u'输入新的日期，格式为YYYYMMDD：')
    QJZ_date = input('')  # 暂存日期，后面的if都是差错用的，因为我不习惯try
    if not QJZ_date.isdigit():  # 检查是不是纯数字
        print(u'YYYYMMDD就是年月日8个数字连起来，中间不能用字符或符号，明白？重输吧。')
        return 'y'
    if len(QJZ_date) != 8:  # 检查是不是8位数
        print(u'你穿越了么！你的位数对吗！重来！')
        return 'y'
    QJZ_year = int(QJZ_date[0:4])  # 检查是不是2013-2030年
    if QJZ_year not in range(2013, 2031):
        print(u'你是从哪里穿越来的！重来！')
        return 'y'
    QJZ_month = int(QJZ_date[4:6])  # 检查是不是正确的月份
    if QJZ_month not in range(1, 13):
        print(u'这是什么奇怪的月份？重来！')
        return 'y'
    QJZ_day = int(QJZ_date[6:8])  # 检查是不是正确的日期
    if QJZ_day not in range(1, 32):
        print(u'这是什么奇怪的日期？重来！')
        return 'y'
    try:  # 最后用try...except兜底
        datetime.date(QJZ_year, QJZ_month, QJZ_day).weekday()
    except ValueError:
        print(u'真的有这个日期么？日历上并没有查到，再来一次。')
        return 'y'

    print(u"修改后的日期是：\n{}年{}月{}日，{}\n再看一眼没错吧？错了重新输入，别让校对捉住了。重来么？（yes/No）".format(
        QJZ_year, QJZ_month, QJZ_day, get_weekday(datetime.date(QJZ_year, QJZ_month, QJZ_day))
    ))

    quit = input('')  # 判断是否退出
    quit += '_'  # 允许用户直接按Enter键跳过
    if quit[0] == 'y' or quit[0] == 'Y':
        return 'y'

    # 分割年月日
    QJZ_year = int(QJZ_date[0:4])
    QJZ_month = int(QJZ_date[4:6])
    QJZ_day = int(QJZ_date[6:8])
    QJZ_weekday = datetime.date(QJZ_year, QJZ_month, QJZ_day).weekday()# 更新周

    # 判断是否为周五或周日
    if QJZ_weekday == 4 or QJZ_weekday == 6:
        print(u'你是Z么，周五和周日停刊啊！再来重新输入一遍。')
        return 'y'

    # 将年月日转化成文本
    str_QJZ_year = str(QJZ_year)
    if QJZ_month < 10:  # 这里如果月/日小于10，则补“0”
      str_QJZ_month = '0' + str(QJZ_month)
    else:
      str_QJZ_month = str(QJZ_month)
    if QJZ_day < 10:
        str_QJZ_day = '0' + str(QJZ_day)
    else:
        str_QJZ_day = str(QJZ_day)

    # 文件名YYYYMMDD
    processFile = str_QJZ_year + str_QJZ_month + str_QJZ_day
    return processFile
