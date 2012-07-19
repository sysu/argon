#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('..')

import tornado.web
from model import manager as mgr
from comm.urls import mark,BaseHandler

# Life is short, code is long.

def _m_error(handler, errmsg):
    handler._tpl['error'] = errmsg
    handler.mrender('m_error.html')
    return True

class MobileBaseHandler(BaseHandler):
    
    def prepare(self):
        super(MobileBaseHandler, self).prepare()
        self._tpl = {}
        self._tpl['msg'] = None 
        self.userid = self._tpl['userid'] = self.current_user
    
    def fail_and_redirect(self, name, errmsg, redirect_path, expire):
        self.set_secure_cookie(name, errmsg, expire)
        self.redirect(redirect_path)
        
    def mrender(self, tpl_name):
        tpl_name = 'mobile/' + tpl_name
        self.render(tpl_name, **self._tpl)


@mark('MobileIndexHandler')
class MobileIndexHandler(MobileBaseHandler):
    
    def get(self):
        self._tpl['top'] = []
        self.mrender('m_index.html')  
   
@mark('MobileLoginHandler')
class MobileLoginHandler(MobileBaseHandler):

    def get(self):
        self._tpl['ref'] = self.ref
        self.mrender('m_login.html')
    
    def post(self):
        userid = self.get_argument('userid', None)
        origref = self.get_argument('ref', None) 
        if userid.isalpha():
            passwd = self.get_argument('password') 
            res = mgr.auth.login(userid, passwd, self.remote_ip)
            if hasattr(res, 'userid') and res.userid.lower() == userid.lower():
                self.set_secure_cookie('userid', userid)
                self.set_secure_cookie('sessionid', res.seid)
                if origref and 'login' not in origref: self.redirect(origref)
                else: self.redirect('/m/')
        self._tpl['msg'] = u'用户名或密码错误'
        self._tpl['ref'] = origref
        self.mrender('m_login.html')

@mark('MobileLogoutHandler')
class MobileLogoutHandler(MobileBaseHandler):
    
    def get(self):
        userid = self.current_user
        if not userid:
            self.redirect('/m/')
        sid = self.get_secure_cookie('sessionid')
        mgr.auth.logout(userid, sid)
        self.clear_all_cookies()
        self.redirect('/m/') 

@mark('MobileBoardHandler')
class MobileBoardHandler(MobileBaseHandler):

    def get(self):
        sections = mgr.section.get_all_section()
        for s in sections:
            # todo: filter those userid has not perm
            s['boards'] = mgr.board.get_by_sid(s.sid)
        
        self._tpl['sections'] = sections
        self.mrender('m_board.html')

@mark('MobilePostHandler')
class MobilePostHandler(MobileBaseHandler):
   
    page_size = 25

    def get(self, boardname, start=0):
        board = mgr.board.get_board(boardname)
        if not board:
            return _m_error(self, u'版面不存在')

        # if has_read_perm
        plist = mgr.post.get_posts(boardname, start, -25)
        for p in plist:
            p.unread = 1 if mgr.readmark.is_read(self.userid, \
                    boardname, p.pid) else 0

        self._tpl['plist'] = plist
        self._tpl['board'] = board
        empty = not len(plist) > 0 
        self._tpl['prev'] = None if empty else mgr.post.prev_post_pid(plist[0].pid) 
        self._tpl['next'] = None if empty else mgr.post.next_post_pid(plist[-1].pid)

        self.mrender('m_listpost.html')

@mark('MobileNewPostHandler')
class MobileNewPostHandler(MobileBaseHandler):
    
    def get(self, boardname):
        if not self.userid:
            self.set_secure_cookie('msg', u'请登陆先')
            self.redirect('/m/login/')
        board = mgr.board.get_board(boardname)
        if not board: _m_error(self, u'没有这个版哦～')

        # todo: if userid has post perm  
        self._tpl['board'] = board
        self.mrender('m_newpost.html')
    
    def post(self, boardname):
        
        self.write('=______=')

@mark('MobileDataHandler')
class MobileDataHandler(MobileBaseHandler):

    def get(self):
        self.mrender('m_data.html')


@mark('MobileAboutHandler')
class MobileAboutHandler(MobileBaseHandler):

    def get(self):
        self.mrender('m_about.html')



