#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('..')

import tornado.web
from model import manager as mgr
from comm.urls import mark,BaseHandler

class MobileBaseHandler(BaseHandler):
    
    def prepare(self):
        super(MobileBaseHandler, self).prepare()
        self.tpl_setting = {}
        self.tpl_setting['userid'] = self.current_user
        self.tpl_setting['msg'] = self.get_secure_cookie('msg') 
    
    def fail_and_redirect(self, name, errmsg, redirect_path, expire):
        self.set_secure_cookie(name, errmsg, expire)
        self.redirect(redirect_path)

@mark('MobileIndexHandler')
class MobileIndexHandler(MobileBaseHandler):
    
    def get(self):
        self.render('mobile/m_index.html', top=[], **self.tpl_setting)  

   
@mark('MobileLoginHandler')
class MobileLoginHandler(MobileBaseHandler):

    def get(self):
        self.render('mobile/m_login.html', ref=self.ref, **self.tpl_setting)
    
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
                return 
        self.tpl_setting['msg'] = u'用户名或密码错误'
        self.render('mobile/m_login.html', ref=origref, **self.tpl_setting)

@mark('MobileLogoutHandler')
class MobileLogoutHandler(MobileBaseHandler):
    
    def get(self):
        userid = self.current_user
        if not userid:
            self.redirect('/m/')
            return 
        sid = self.get_secure_cookie('sessionid')
        mgr.auth.logout(userid, sid)
        self.clear_all_cookies()
        self.redirect('/m/') 

@mark('MobileBoardHandler')
class MobileBoardHandler(MobileBaseHandler):

    def get(self):
        sections = mgr.section.get_all_section()
        for s in sections:
            s['boards'] = mgr.board.get_by_sid(s.sid)

        self.render('mobile/m_board.html', sections=sections, **self.tpl_setting)


@mark('MobileDataHandler')
class MobileDataHandler(MobileBaseHandler):

    def get(self):
        self.render('mobile/m_data.html', **self.tpl_setting)


@mark('MobileAboutHandler')
class MobileAboutHandler(MobileBaseHandler):

    def get(self):
        self.render('mobile/m_about.html', **self.tpl_setting)





