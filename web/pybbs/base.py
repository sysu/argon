#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('..')


import tornado.web
from model import manager as mgr
from comm.urls import mark,BaseHandler

class PBaseHandler(BaseHandler):

    def prepare(self):
        super(PBaseHandler, self).prepare()
        self._tpl = {}

    def fail_and_redirect(self, name, errmsg, redirect_path, expire):
        self.set_secure_cookie(name, errmsg, expire)
        self.redirect(redirect_path)

    def mrender(self, tpl_name):
        tpl_name = 'standard/' + tpl_name
        self.render(tpl_name, **self._tpl)


