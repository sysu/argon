#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import tornado.web
from model import manager as mgr
from urls import BaseHandler,mark
from funcs import *

@mark('CommAjaxGetPostHandler')
class CommAjaxGetPostHandler(BaseHandler):

    def get(self, boardname, pid):
        
        board = None if not boardname.isalpha() \
                else mgr.board.get_board(boardname)
        
        result = {}
        if board is None:
           result['success'] = False
           result['content'] = u'版面不存在';
           return self.write(result)
       
        #todo: if userid has read perm

        post = mgr.post.get_post(boardname, pid)

        result['success'] = True
        if post: 
            for k,v in post.items():
                try:
                    v = str(v)
                except:
                    pass
                result[k] = self.xhtml_escape(v)
        else: 
            result['content'] = u'本帖子不存在或者已被删除'
        
        if self.userid:
            mgr.readmark.set_read(self.userid, boardname, pid)

        self.write(result)

@mark('CommAjaxGetQuoteHandler')
class CommAjaxGetQuoteHandler(BaseHandler):
    
    def get(self, boardname, pid):
        
        board = None if not boardname.isalpha() \
                else mgr.board.get_board(boardname)
        
        result = {}
        if board is None:
           result['success'] = False
           result['content'] = u'版面不存在';
           return self.write(result)
            
        # todo: if userid has read perm
        post = mgr.post.get_post(boardname, pid)
        
        if not post:
            result['success'] = False
            result['content'] = u'本帖子不存在或者已被删除'
            return self.write(result)
        
        quote = fun_gen_quote(post['userid'], post['content'])

        content = post['content']
        result['success'] = True
        result['_xsrf'] = self.xsrf_token
        result['content'] = self.xhtml_escape(quote)
        self.write(result)

@mark('CommAjaxNewPostHandler')
class CommAjaxNewPostHandler(BaseHandler):

    def post(self, boardname):
        
        result = {}
        if not self.userid: 
            return self.write({'success':False, 'content':u'请先登陆'})
        board = mgr.board.get_board(boardname)
        if not board: 
            return self.write({'success':False, 'content':u'版面不存在'})

        # todo: if has post perm and allow to reply
        title = self.get_argument('title')
        content = self.get_argument('content')
        replyid = self.get_argument('replyid')

        res = mgr.action.reply_post(boardname = boardname, \
                userid = self.userid,
                title=title,\
                content = content,\
                addr = self.remote_ip,\
                host = 'TestLand',\
                replyid = replyid)
        if res: 
            result['success'],result['conent'] = True, u'发表成功'
        else:
            result['success'],result['conent'] = False, u'发表失败'
        
        self.write(result)


@mark('CommAjaxGetMailHandler')
class CommAjaxGetMailHandler(BaseHandler):
    
    def get(self, mid):
        
        if not self.userid: self.login_page() 
        result = {}
        uid = mgr.userinfo.name2id(self.userid)
        mail = mgr.mail.one_mail(uid, mid)
        
        if mail: 
            result['success'] = True
            mgr.mail.set_read(uid, mid)
            for k,v in mail.items():
                try:
                    v = str(v)
                except:
                    pass
                result[k] = self.xhtml_escape(v)
        else: 
            result['success'] = False 
            result['content'] = u'本帖子不存在或者已被删除'
        
        self.write(result)

@mark('CommAjaxGetBoardHandler')
class CommAjaxGetBoardHandler(BaseHandler):
    
    def get(self, sid):

        result = {}
        boards = mgr.board.get_by_sid(sid)
        
        if not boards:
            result['success'] = False
            result['boards'] = []
            self.write(result)
        result['success']  = True
        result['boards'] = []
        for b in boards:
            # todo: if userid has read perm 
            result['boards'].append(b.boardname)
        
        self.write(result)

@mark('CommAjaxCheckMailHandler')
class CommAjaxCheckMailHandler(BaseHandler):
    
    def get(self):

        if not self.userid:
            self.write({'success': False, 'content': '0'})
        new_mail = mgr.action.get_new_mail(self.userid, 0, 1)
            
        result = {}
        result['success'] = True
        result['content'] = '1' if new_mail else '0'
        
        self.write(result)

