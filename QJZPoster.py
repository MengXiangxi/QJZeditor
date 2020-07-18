#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 21:37:13 2020

@author: KakaHiguain@BDWM
"""

import getpass
import os
import re
import time

from BDWM import BDWM
from QJZCrawler import QJZCrawler
from QJZEditor_2_3_1_py3k import main as editor_main
from utils import bold_string, bold_green, bold_red, bold_yellow, wrap_separate_bar


class QJZPoster:
    _BOARD_NAME_MAP = ['WMReview', 'WMQJZ', 'Test']
    # WMReview版精华区“历期起居注”的路径
    _WMREVIEW_COLLECTION_PATH = 'groups/GROUP_0/WMReview/D5448A5D2'
    # 转到BBSInfo时要加上这一句
    _FORWARD_POST_HEADER = '原文由 WMWZ 发表在 WMReview 版 >>>\n'

    def __init__(self):
        print(bold_string('Hi, 欢迎使用全自动机器人起居注主编~~'))
        today = time.strftime('%Y%m%d', time.localtime(time.time()))
        res = input('请输入今天的日期(YYYYMMDD)，默认为今天({})：'.format(today))
        if res == '':
            res = today
        while len(res) != 8 or not res.isdigit():
            res = input(bold_red('无效的日期！请重新输入：'))
        self._date = res
        password = getpass.getpass("请输入WMWZ的密码(不会显示)：")
        self._bdwm = BDWM('WMWZ', password)
        
        self._year, self._month, self._day = \
            self._date[:4], self._date[4:6], self._date[6:]
        self._title = '未名起居注 {}年{}月{}日'.format(
            self._year, self._month, self._day)
        self._txt_file = os.path.join('QJZ@{}'.format(self._date), 
                                      'QJZ@{}.txt'.format(self._date))
        
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
        self._bdwm.edit_post('BBSInfo', 
                             bbsinfo_postid, 
                             self._title, 
                             self._FORWARD_POST_HEADER + self._post_content_string,
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
    
    def _auto_post_pipeline(self, num):
        """自动发帖的工序"""
        board_name = self._BOARD_NAME_MAP[num]
        postid, threadid = self._create_post(board_name)
        
        if num == 0:
            self._operate_post(board_name, postid)
            self._forward_to_three_boards(board_name, postid)
            self._add_into_collection(board_name, postid, threadid)

        if num == 1:
            input('请at校对进行review，校对结束点回车确认')
            ans = input('是否需要正式出刊(即发往WMReview版)？(yes/No)')
            if ans and ans[0] in ['y', 'Y']:
                print('请根据校对建议，修改好电脑上的{}文件！'.format(self._txt_file))
                input('按任意键正式出刊~')
                self._auto_post_pipeline(0)

    def main(self):
        """主过程"""
        print(bold_string("在执行程序之前，请检查各区的帖子标题、格式是否正确，帖子正文里无采编内容外其他信息。"))
        print('标题正确格式："X@MMDD" / "X@MMDD kong" / "X@MMDD void"')
        print(bold_yellow("注：由于院士代码的限制，当我们找到同一个区的多个帖子时（如有多个8@0328），"
              "我们只保留发表时间最后的主题帖。如果有需要合并多个采编的爆料，请手动修改版上的帖子。"))
        input("按任意键开始爬取帖子~")

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

        while True:
            print(bold_string(wrap_separate_bar('开始跑院士的脚本')))
            try:
                editor_main()
            except Exception:
                ans = input('院士脚本报错，请【将种子文件修改正确后】输入y重跑脚本；按任意键退出程序:')
                if ans and ans[0] in ['y', 'Y']:
                    continue
                else:
                    return
            break

        print(bold_string(wrap_separate_bar('院士脚本跑完啦，接下来开始帮你自动发帖')))
        num = input('请选择你要发贴的版面代号 0.WMReview(正式出刊), 1.WMQJZ(给校对看), 2.Test(测试)：')
        while num not in {'0', '1', '2'}:
            num = input(bold_red('请输入0，1或2！==>'))
        self._auto_post_pipeline(int(num))

        input('按任意键结束~')

                
if __name__ == '__main__':
    poster = QJZPoster()
    poster.main()
