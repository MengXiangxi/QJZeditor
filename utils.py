#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 21:37:13 2020

@author: KakaHiguain@BDWM
"""

import datetime

SEPARATE_BAR = "======================"
NO_QJZ_WEEKDAYS = {4, 6}  # Friday and Sunday
CHINESE_WEEKDAY = {
    0: u'星期一',
    1: u'星期二',
    2: u'星期三',
    3: u'星期四',
    4: u'星期五',
    5: u'星期六',
    6: u'星期日',
}


def get_content_from_raw_string(content_string):
    parts = content_string.split('\u001B[')
    change_font = content_string.startswith('\u001B[')
    template = '{{"type":"ansi","bold":{},"underline":{},"fore_color":{},' \
               '"back_color":{},"content":"{}"}}'
    bold, underline, fore_color, back_color = 'false', 'false', 9, 9
    res = []
    for part in parts:
        pos = part.find('m')
        # The first part may not change font.
        if not change_font:
            pos = -1
            change_font = True
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


def change_date():
    """Return a 8 digit date if input is invalid, otherwise return None."""
    print(u'输入新的日期，格式为YYYYMMDD：')
    QJZ_date = input('')  # 暂存日期，后面的if都是差错用的，因为院士不习惯try
    if not QJZ_date.isdigit():  # 检查是不是纯数字
        print(u'YYYYMMDD就是年月日8个数字连起来，中间不能用字符或符号，明白？重输吧。')
        return None
    if len(QJZ_date) != 8:  # 检查是不是8位数
        print(u'你穿越了么！你的位数对吗！重来！')
        return None
    QJZ_year = int(QJZ_date[0:4])  # 检查是不是2013-2030年
    if QJZ_year not in range(2013, 2031):
        print(u'你是从哪里穿越来的！重来！')
        return None
    QJZ_month = int(QJZ_date[4:6])  # 检查是不是正确的月份
    if QJZ_month not in range(1, 13):
        print(u'这是什么奇怪的月份？重来！')
        return None
    QJZ_day = int(QJZ_date[6:8])  # 检查是不是正确的日期
    if QJZ_day not in range(1, 32):
        print(u'这是什么奇怪的日期？重来！')
        return None
    try:  # 最后用try...except兜底
        QJZ_weekday = datetime.date(QJZ_year, QJZ_month, QJZ_day).weekday()
    except ValueError:
        print(u'真的有这个日期么？日历上并没有查到，再来一次。')
        return None

    # 判断是否为周五或周日
    if QJZ_weekday in NO_QJZ_WEEKDAYS:
        print(u'你是Z么，周五和周日停刊啊！再来重新输入一遍。')
        return None

    print(u"修改后的日期是：\n{}年{}月{}日，{}\n再看一眼没错吧？错了重新输入，别让校对捉住了。重来么？（yes/No）".format(
        QJZ_year, QJZ_month, QJZ_day, CHINESE_WEEKDAY[QJZ_weekday]
    ))

    quit = input('')  # 判断是否退出
    quit += '_'  # 允许用户直接按Enter键跳过
    if quit[0] == 'y' or quit[0] == 'Y':
        return None

    return QJZ_date


def get_QJZ_date():
    today = datetime.date.today()

    # 日期 YYYYMMDD
    QJZ_date = today.__format__('%Y%M%D')
    QJZ_weekday = today.weekday()

    description = u"今天是{}年{}月{}日，{}\n".format(
        today.year, today.month, today.day, CHINESE_WEEKDAY[QJZ_weekday])
    # 打印出来默认的日期
    if QJZ_weekday in NO_QJZ_WEEKDAYS:
        print(description + u"今日停刊。")
        should_change_date = 'y'
    else:
        print(description + u"默认排版今天的。要更改排版起居注的日期么？(yes/No):")
        should_change_date = input('')  # 判断是否更改日期
        should_change_date += '_'  # 允许用户直接按Enter键跳过
    # 手动更新年月日
    if should_change_date[0] in {'y', 'Y'}:
        QJZ_date = None
        while not QJZ_date:
            QJZ_date = change_date()

    return QJZ_date
