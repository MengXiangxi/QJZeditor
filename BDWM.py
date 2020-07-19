#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 21:37:13 2020

@author: KakaHiguain@BDWM
"""

from hashlib import md5
import json
import requests

from utils import get_content_from_raw_string, bold_green, bold_red


class BDWM:
    _HOST = 'bbs.pku.edu.cn'
    _BOARD_MODES = {'topic', 'single'}
    _BID_MAP = {  # Keys should be in lower case.
        'sysop': 1,
        'test': 7,
        'triangle': 22,
        'football': 93,
        'wmqjz': 306,
        'bbsinfo': 352,
        'sports_game': 519,
        'wmreview': 728,
        'sandbox': 779,
    }

    _POST_ACTION_NAME = {
        'mark': '保留',
        'unmark': '取消保留',
        'digest': '文摘',
        'undigest': '取消文摘',
        'top': '置顶',
        'untop': '取消置顶',
        'highlight': '高亮',
        'unhighlight': '取消高亮',
    }
    
    def __init__(self, id, passwd):
        self._id = id
        self._passwd = passwd
        self._session = requests.session()
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/80.0.3987.122 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': self._HOST,
            'X-Requested-With': 'XMLHttpRequest',
        }
        skey, self._uid = self._login()
        self._cookie = 'skey={}; uid={}'.format(skey, self._uid)
        self._headers["Cookie"] = self._cookie
    
    def _get_action_url(self, action_name):
        return 'https://{}/v2/{}.php'.format(self._HOST, action_name)
        
    def _login(self):
        token = md5('{1}{0}{1}'.format(self._id, self._passwd).encode('utf8'))
        data = {
            "username": self._id,
            "password": self._passwd,
            "keepalive": '0',
            "t": token.hexdigest()
        }
        self._get_response_data('ajax/login', data, '登录')
        
        requests.cookies.RequestsCookieJar()
        cookies_dict = self._session.cookies.get_dict()
        return cookies_dict['skey'], cookies_dict['uid']

    # Functions for getting page.
    def _get_page_content(self, url):
        return self._session.post(url, headers=self._headers).text
    
    def get_board_page(self, board_name, page=1, mode='topic'):
        assert mode in self._BOARD_MODES, "Not a correct mode!"
        page_url = '{}?bid={}&mode={}&page={}'.format(
            self._get_action_url('thread'), self._BID_MAP[board_name.lower()], mode, page)
        return self._get_page_content(page_url)

    def get_single_post_page(self, board_name, postid):
        page_url = '{}?bid={}&postid={}'.format(
            self._get_action_url('post-read-single'), self._BID_MAP[board_name.lower()], postid)
        return self._get_page_content(page_url)

    def get_post_page(self, board_name, threadid):
        page_url = '{}?bid={}&threadid={}'.format(
            self._get_action_url('post-read'), self._BID_MAP[board_name.lower()], threadid)
        return self._get_page_content(page_url)

    # Functions for getting action response.
    def _get_response_data(self, relative_url, data, action_string):
        response_data = json.loads(
            self._session.post(self._get_action_url(relative_url), 
                               headers=self._headers,
                               data=data).text)
        assert response_data['success'], bold_red(action_string + '失败！')
        return response_data

    @classmethod
    def _get_post_info(cls, mail_re, no_reply, parent_id):
        post_info = '"no_reply":{},"mail_re":{}'.format(str(no_reply).lower(), str(mail_re).lower())
        if parent_id:
            post_info += ',"parentid":{}'.format(parent_id)
        return '{{{}}}'.format(post_info)

    def create_post(self, board_name, title, content_string,
                    mail_re=True, no_reply=False, signature=None, parent_id=None):
        content = get_content_from_raw_string(content_string)
        bid = self._BID_MAP[board_name.lower()]

        data = {
            'title': title,
            'content': content,
            'bid': bid,
            'postinfo': self._get_post_info(mail_re, no_reply, parent_id),
        }
        if signature is not None:
            data['signature'] = signature

        action = '回帖' if parent_id else '发帖'
        response_data = self._get_response_data('ajax/create_post', data, action)
        postid = response_data['result']['postid']
        post_link = '{}?bid={}&postid={}'.format(
            self._get_action_url('post-read-single'), bid, postid)
        print(bold_green(action + '成功！') + '帖子链接：{}'.format(post_link))
        return response_data['result']

    def reply_post(self, board_name, main_postid, main_title, content_string,
                   mail_re=True, no_reply=False, signature=None):
        """Reply to the post with main_postid and main_title"""
        return self.create_post(board_name, "Re: " + main_title, content_string,
                                mail_re, no_reply, signature, parent_id=main_postid)

    def edit_post(self, board_name, postid, title, content_string, signature=None):
        content = get_content_from_raw_string(content_string)
        bid = self._BID_MAP[board_name.lower()]
        data = {
            'title': title,
            'content': content,
            'bid': bid,
            'postid': postid,
            'postinfo': '{}',
        }
        if signature is not None:
            data['signature'] = signature
        self._get_response_data('ajax/edit_post', data, '修改帖子')
        post_link = '{}?bid={}&postid={}'.format(
            self._get_action_url('post-read-single'), bid, postid)
        print(bold_green('修改帖子成功！') + '帖子链接：{}'.format(post_link))
        
    def forward_post(self, from_board_name, to_board_name, postid):
        data = {
            'from': 'post',
            'bid': self._BID_MAP[from_board_name.lower()],
            'postid': postid,
            'to': 'post',
            'tobid': self._BID_MAP[to_board_name.lower()]
        }
        self._get_response_data('ajax/forward', 
                                data, 
                                '转帖到{}版'.format(to_board_name))
        print(bold_green('已成功转发到{}版！'.format(to_board_name)))
    
    def operate_post(self, board_name, postid_list, action):
        assert action in self._POST_ACTION_NAME, '无效的帖子操作！'
        data = {
            "bid": self._BID_MAP[board_name.lower()],
            "list": '[{}]'.format(','.join(postid_list)),
            "action": action
        }
        self._get_response_data(
            'ajax/operate_post', data, 
            '{}帖子'.format(self._POST_ACTION_NAME[action]))
        print(bold_green('{}帖子成功！'.format(self._POST_ACTION_NAME[action])))

    def get_collection_items(self, path):
        data = {"path": path}
        collection_items = {}
        response_data = self._get_response_data('ajax/get_collection_items', data, '获取精华区目录')
        for directory in response_data["result"]:
            if directory["isdir"]:
                collection_items[directory["title"]] = directory['path']
        return collection_items

    def create_collection_dir(self, path, title, bms=''):
        data = {
            "base": path,
            "title": title,
            "bms": bms
        }
        response_data = self._get_response_data('ajax/create_collection_dir', data, '创建精华区目录')
        print(bold_green('已创建精华区目录 "{}"'.format(title)))
        return response_data['name']

    def add_new_collection(self, board_name, postid, threadid, path):
        data = {
            "from": "post",
            "bid": self._BID_MAP[board_name.lower()],
            "postid": postid,
            "threadid": threadid,
            "base": path
        }
        response_data = self._get_response_data('ajax/collection_import', data, '添加精华区文件')
        print(bold_green('添加精华区文件成功！'))
        return response_data['name']       
