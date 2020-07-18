#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 1 09:53:22 2020

@author: KakaHiguain@BDWM
"""

import os
import re

from bs4 import BeautifulSoup


class QJZCrawler:
    _WMQJZ_BOARD_NAME = 'WMQJZ'
    _MAX_PAGES_TO_SEARCH = 6

    def __init__(self, bdwm, year, month, day):
        self._bdwm = bdwm
        self._date = month + day
        self._seed_filename = '{}{}.txt'.format(year, self._date)
        if os.path.exists(self._seed_filename):
            os.remove(self._seed_filename)

    @classmethod
    def _extract_from_post_page(cls, post_page):
        """Return username and post content lines from post_page html."""
        post_soup = BeautifulSoup(post_page, features="html.parser")

        username_body = post_soup.find('div', attrs={'class': 'post-owner'}) \
                                 .find('p', attrs={'class': 'username'})
        content_body = post_soup.find('div', attrs={'class': 'body file-read image-click-view'})
        post_lines = []
        for line in content_body.find_all('p'):
            post_lines.append(line.string.replace('\xa0', ' ') if line.string else '')
        return username_body.a.string, post_lines

    @classmethod
    def _output_into_file(cls, f, username, post_title, post_lines):
        """Output post info to seed file."""
        lines = [
            "发信人: {}".format(username),
            "标  题: {}".format(post_title),
            "发信站:",
            "",
        ]
        lines.extend(post_lines)
        lines.append('--')

        last_line = ''
        for line in lines:
            # Skip "comment" lines.
            if line.startswith('#') or line.startswith('//'):
                continue
            # Avoid writing two consecutive blank lines.
            if last_line or line:
                # Need to use \r\n for windows linefeed.
                f.write(line + '\r\n')
            last_line = line

    def generate_seed_file(self):
        """Generate seed file according to the posts on WMQJZ,
        return whether generate successfully."""
        section_set = set()
        postid_list = []
        for page in range(1, self._MAX_PAGES_TO_SEARCH + 1):
            board_page = self._bdwm.get_board_page(self._WMQJZ_BOARD_NAME, page, mode='single')
            board_soup = BeautifulSoup(board_page, features="html.parser")
            for post in board_soup.find_all('div', attrs={"class": "list-item-single list-item"}):
                postid = post['data-itemid']
                if int(postid) < 0:
                    continue
                post_title = post.find('div', attrs={"class": "title l limit"}) \
                                 .string.replace('\xa0', ' ')
                pattern = r'^([0-9A-DF-H])@' + self._date
                match_res = re.search(pattern, post_title)
                if not match_res:
                    continue

                # 0-9, A, B, C, D, F, G, H
                section = match_res.group(1)
                print("找到{}，帖子id：{}".format(post_title, postid))
                if section in {"D", "F"}:
                    print("暂不支持采{}区，跳过该帖子~".format(section))
                    continue
                if section in section_set:
                    print("{}区已经存在，跳过该帖子~".format(section))
                    continue
                section_set.add(section)
                postid_list.append(postid)

                post_page = self._bdwm.get_single_post_page(self._WMQJZ_BOARD_NAME, postid)
                username, post_lines = QJZCrawler._extract_from_post_page(post_page)
                print("{}区采编：{}".format(section, username))
                with open(self._seed_filename, "a", newline="") as f:
                    QJZCrawler._output_into_file(f, username, post_title, post_lines)

        missing_sections = []
        for section_num in range(10):
            if str(section_num) not in section_set:
                missing_sections.append(section_num)
        if missing_sections:
            print("以下分区未能找到帖子：{}".format(str(missing_sections)))
            return False
        print("已生成种子文件{}，请查看~".format(self._seed_filename))
        self._bdwm.operate_post(self._WMQJZ_BOARD_NAME, postid_list, 'digest')
        print("已将找到的各区帖子g上。")
        return True
