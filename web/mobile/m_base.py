#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('..')

import tornado.web
from model import manager as mgr
from comm.urls import mark,BaseHandler

def m_error(handler, errmsg):
    handler._tpl['error'] = errmsg
    handler.mrender('m_error.html')
    return True

def fa(msg):
    # todo: filter ascii control character
    return msg

class MobileBaseHandler(BaseHandler):
    
    def prepare(self):
        super(MobileBaseHandler, self).prepare()
        self._tpl = {}
        msg = self.get_secure_cookie('msg')
        self.clear_cookie('msg') 
        self._tpl['msg'] = msg 
        self._tpl['userid'] = self.current_user
    
    def fail_and_redirect(self, name, errmsg, redirect_path, expire):
        self.set_secure_cookie(name, errmsg, expire)
        self.redirect(redirect_path)
        
    def mrender(self, tpl_name):
        tpl_name = 'mobile/' + tpl_name
        self.render(tpl_name, **self._tpl)
    
    def login_page(self):
        self.set_secure_cookie('msg', u'请登陆先')
        self.redirect('/m/login/')


