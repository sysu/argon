#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import tornado.web
from model import manager as mgr
from m_base import *

@mark('MobileAjaxGetPostHandler')
class MobileAjaxGetPostHandler(MobileBaseHandler):

    def get(self, boardname, pid):
        
        board = None if not boardname.isalpha() \
                else mgr.board.get_board(boardname)
        
        result = {}
        if board is None:
           result['success'] = False
           result['content'] = u'版面不存在';
           return self.write(result)
        
        post = mgr.post.get_post(boardname, pid)

        result['success'] = True
        if post: result['content'] = post['content']
        else: result['content'] = u'本帖子不存在或者已被删除'

        self.write(result)

@mark('MobileAjaxGetQuoteHandler')
class MobileAjaxGetQuoteHandler(MobileBaseHandler):

    def get(self, boardname, pid):
        
        board = None if not boardname.isalpha() \
                else mgr.board.get_board(boardname)
        
        result = {}
        if board is None:
           result['success'] = False
           result['content'] = u'版面不存在';
           return self.write(result)
        
        post = mgr.post.get_post(boardname, pid)
        
        if not post:
            result['success'] = False
            result['content'] = u'本帖子不存在或者已被删除'
            return self.write(result)

        content = post['content']
        owner = mgr.userinfo.get_user(post['owner'])
        if not owner: owner['userid'] = owner['nickname'] = 'No such user' 
    
        pattern = u'【 在 %s ( %s ) 的大作中提到: 】' % \
                ( owner['userid'], owner['nickname'] )
    
        quote = pattern + '\n' + '\n'.join(map(lambda l: u'：'+l, content.split('\n')))

        result['success'] = True
        result['content'] = quote
        self.write(result)

