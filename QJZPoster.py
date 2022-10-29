#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 21:37:13 2020

@author: KakaHiguain@BDWM
"""

import base64
import getpass
import os
import re
import traceback

from BDWM import BDWM
from QJZCrawler import QJZCrawler
from QJZEditor_2_3_1_py3k import main as editor_main
from utils import bold_string, bold_green, bold_red, bold_yellow, wrap_separate_bar, \
    get_QJZ_date, get_editors_info, initialize


class QJZPoster:
    _BOARD_NAME_MAP = ['WMReview', 'WMQJZ', 'Test']
    # WMReview版精华区“历期起居注”的路径
    _WMREVIEW_COLLECTION_PATH = 'groups/GROUP_0/WMReview/D5448A5D2'
    _INITIALIZE_FILE = os.path.join(os.path.dirname(__file__), '.initialized')
    _MAXIMUM_TITLE_LENGTH = 20

    def __init__(self):
        print(bold_string('Hi, 欢迎使用全自动机器人起居注主编~~'))
        if not os.path.exists(self._INITIALIZE_FILE):
            _, editoraddlist, editordictupper = get_editors_info()
            initialize(editoraddlist, editordictupper)
            with open(self._INITIALIZE_FILE, 'w'):
                pass

        self._date = get_QJZ_date()

        password_file = os.path.join(os.path.dirname(__file__), '.token', 'token')
        password = self._get_decoded_password(password_file)
        if not password:
            password = getpass.getpass("请输入WMWZ的密码(不会显示)：")
            # Store encoded password in a file, to avoid inputting password every time.
            self._write_encoded_password(password, password_file)

        try:
            self._bdwm = BDWM('WMWZ', password)
        except BDWM.RequestError as e:
            # If failing to login, remove wrong password file.
            os.remove(password_file)
            raise e
        
        self._year, self._month, self._day = \
            self._date[:4], self._date[4:6], self._date[6:]
        self._title = '未名起居注 {}年{}月{}日'.format(
            self._year, self._month, self._day)
        self._origin_title = self._title
        self._txt_file = os.path.join('QJZ@{}'.format(self._date), 
                                      'QJZ@{}.txt'.format(self._date))
        self._seed_file = '{}.txt'.format(self._date)

    @classmethod
    def _get_decoded_password(cls, file):
        """read password and decode it"""
        if not os.path.exists(file):
            return None
        with open(file, 'r') as f:
            encoded_password = f.read()
        return base64.b64decode(encoded_password.encode()).decode()

    @classmethod
    def _write_encoded_password(cls, password, file):
        """encode password and write it"""
        encoded_password = base64.b64encode(password.encode()).decode()
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w') as f:
            f.write(encoded_password)

    def _create_post(self, board_name):
        """在board_name版发本期起居注"""
        with open(self._txt_file, 'r', encoding='utf8') as f:
            self._post_content_string = f.read()

        result = self._bdwm.create_post(board_name, 
                                        self._title, 
                                        self._post_content_string, 
                                        signature=0)
        return result['postid'], result['threadid']

    def _operate_post(self, board_name, postid):
        """对本期起居注做m, g, 置顶等操作"""
        assert board_name == 'WMReview'
        # 取消上一期置顶
        wmreview_page = self._bdwm.get_board_page('WMReview', mode='topic')
        pattern = r'<div class="list-item" data-itemid="([0-9]*)">'
        last_postid = max(map(lambda m: int(m.group(1)), 
                              re.finditer(pattern, wmreview_page)))        
        self._bdwm.operate_post(board_name, [str(last_postid)], 'untop')
        
        # m, g, 置顶
        for action in ['mark', 'digest', 'top']:
            self._bdwm.operate_post(board_name, [str(postid)], action)

    def _forward_to_three_boards(self, board_name, postid):
        """将本期起居注转发到指定的三个版面"""
        input('按任意键一键转发到BBSInfo, Triangle和sysop')
        for to_board_name in ['BBSInfo', 'Triangle', 'sysop']:
            self._bdwm.forward_post(board_name, to_board_name, postid)
        
        # 修改BBSInfo版对应帖子的标题
        bbsinfo_page = self._bdwm.get_board_page('BBSInfo', mode='single')
        pattern = r'data-itemid="([0-9]*)"'
        bbsinfo_postid = int(re.search(pattern, bbsinfo_page).group(1))
        # 修改转发头为Term下的转发格式
        with open(os.path.join('header.ans'), 'r', encoding='utf8') as f:
           FORWARD_POST_HEADER = f.read()
        self._bdwm.edit_post('BBSInfo', 
                             bbsinfo_postid, 
                             self._title, 
                             FORWARD_POST_HEADER + '\n' + self._post_content_string,
                             signature=0)
            
    def _add_into_collection(self, board_name, postid, threadid):
        """将本期起居注收精"""
        input('按任意键一键收精')
        dir_name = '{}年{}月'.format(self._year, self._month)
        collection_items = \
            self._bdwm.get_collection_items(self._WMREVIEW_COLLECTION_PATH)
        if dir_name not in collection_items:
            sub_path = self._bdwm.create_collection_dir(self._WMREVIEW_COLLECTION_PATH, dir_name)
        else:
            sub_path = collection_items[dir_name]
        self._bdwm.add_new_collection(
            board_name, postid, threadid, 
            '{}/{}'.format(self._WMREVIEW_COLLECTION_PATH, sub_path))

    @classmethod
    def _get_title_length(cls, title):
        length = len(title)
        utf8_length = len(title.encode('utf-8'))
        return (utf8_length + length) / 2

    def _maybe_change_title(self):
        while True:
            ans = input('发帖标题为：【{}】，是否修改？(yes/No)'.format(self._title))
            if ans and ans[0] in ['y', 'Y']:
                print('请补齐小标题（不超过10个汉字或20个字母，若不需要小标题可留空）：')
                new_suffix = input(self._origin_title + ' ')
                while self._get_title_length(new_suffix) > self._MAXIMUM_TITLE_LENGTH:
                    print('小标题过长，请重新输入：')
                    new_suffix = input(self._origin_title + ' ')

                if new_suffix:
                    self._title = self._origin_title + ' ' + new_suffix
                else:
                    self._title = self._origin_title
            else:
                break

    def _auto_post_pipeline(self, num, reviewer=None):
        """自动发帖的工序"""
        self._maybe_change_title()
        board_name = self._BOARD_NAME_MAP[num]
        postid, threadid = self._create_post(board_name)

        if num == 0:
            self._operate_post(board_name, postid)
            self._forward_to_three_boards(board_name, postid)
            self._add_into_collection(board_name, postid, threadid)

        if num == 1:
            if reviewer:
                content = 'Hi, @{} , 麻烦校对看一下~'.format(reviewer)
                self._bdwm.reply_post(board_name, postid, self._title, content)
                print('已在版面上at校对~', end="")
            input('请在校对结束后点回车确认')
            ans = input('是否需要正式出刊(即发往WMReview版)？(正式出刊输入y，结束程序输入n)')
            while not(ans and ans[0] in ['y', 'Y', 'n', 'N']):
                ans = input('请输入y或n！')
            if ans[0] in ['y', 'Y']:
                print('请根据校对建议，修改好电脑上的{}文件！'.format(self._txt_file))
                self._auto_post_pipeline(0)

    def main(self):
        """主过程"""
        print(bold_string("在执行程序之前，请检查各区的帖子标题、格式是否正确，帖子正文里无采编内容外其他信息。"))
        print('标题正确格式："X@MMDD" / "X@MMDD kong" / "X@MMDD void"')
        print(bold_yellow("注：由于院士代码的限制，当我们找到同一个区的多个帖子时（如有多个8@0328），"
              "我们只保留发表时间最后的主题帖。如果有需要合并多个采编的爆料，请手动修改版上的帖子。"))
        ans = input("按任意键开始爬取帖子~ 【注：若种子文件{}已经生成，请按e跳过该步骤】".format(self._seed_file))
        if not (ans and ans[0] in ['e', 'E']):
            crawler = QJZCrawler(self._bdwm, self._year, self._month, self._day)
            while True:
                print(bold_string(wrap_separate_bar("开始从WMQJZ版爬取帖子：")))
                if crawler.generate_seed_file():
                    break
                print(bold_red("自动爬取帖子失败！请检查各区是否齐全，发帖格式是否正确，后重试~"))
                ans = input("按任意键重新爬取帖子，或输入e退出程序")
                if ans and ans[0] in ['e', 'E']:
                    return
            print(bold_green("爬取帖子完毕！"))

        input("按任意键开始跑院士的脚本~")

        reviewer = None
        while True:
            print(bold_string(wrap_separate_bar('开始跑院士的脚本')))
            try:
                reviewer = editor_main(self._date)
            except Exception:
                print(traceback.format_exc())
                ans = input('院士脚本报错，可能是种子文件格式有误~\n'
                            '请【将种子文件{}修改正确后】输入y重跑脚本；按任意键退出程序:'.format(self._seed_file))
                if ans and ans[0] in ['y', 'Y']:
                    continue
                else:
                    return
            break

        print(bold_string(wrap_separate_bar('院士脚本跑完啦，接下来开始帮你自动发帖')))
        num = input('请选择你要发贴的版面代号 0.WMReview(正式出刊), 1.WMQJZ(给校对看), 2.Test(测试)：')
        while num not in {'0', '1', '2'}:
            num = input(bold_red('请输入0，1或2！==>'))
        self._auto_post_pipeline(int(num), reviewer)

        input('按任意键结束~')

                
if __name__ == '__main__':
    poster = QJZPoster()
    poster.main()
