#!/usr/bin/env python 
# -*- encoding: utf8 -*-

import sys
sys.path.append('..')

import tornado.web
from tornado import escape

class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    @property
    def ch(self):
        return self.application.ch

    @property
    def headers(self):
        return self.request.headers

    def get_current_user(self):
        return self.get_secure_cookie('userid')

    def prepare(self):
        try:
            self.ref = self.headers['Referer']
        except:
            self.ref = ''
        self.remote_ip = self.request.remote_ip
        self.userid = self.current_user
        self.xhtml_escape = escape.xhtml_escape


class Proxy(dict):

    def __call__(self, name):
        def inner_mark(obj):
            self[name] = obj
            obj.__mark__ = name
        return inner_mark

mark = Proxy()

def _import(mod, handler):

    __import__(name=mod, fromlist=handler, level=0)
    return mark[handler]

urls = [

           (r"/", _import("pybbs.index","PIndexHandler")),
           (r"/post/", _import("pybbs.post","PPostHandler")),
           (r"/board/", _import("pybbs.board","PBoardHandler")),

            # ajax
           (r"/a/checkmail/?", _import("comm.ajax","CommAjaxCheckMailHandler")),
           (r"/a/mail/(\d{1,10})/?", _import("comm.ajax","CommAjaxGetMailHandler")),
           (r"/a/board/(\d{1,2})/?", _import("comm.ajax","CommAjaxGetBoardHandler")),
           (r"/a/(\w{2,16})/(\d{1,10})/?", _import("comm.ajax","CommAjaxGetPostHandler")),
           (r"/a/(\w{2,16})/quote/(\d{1,10})/?", _import("comm.ajax","CommAjaxGetQuoteHandler")),
           (r"/a/(\w{2,16})/post/?", _import("comm.ajax","CommAjaxNewPostHandler")),

            # mobile
           (r"/m/?$", _import("mobile.m_main","MobileIndexHandler")),
           (r"/m/login/?$", _import("mobile.m_main","MobileLoginHandler")),
           (r"/m/logout/?$", _import("mobile.m_main","MobileLogoutHandler")),
           (r"/m/brds/?$", _import("mobile.m_main","MobileBoardHandler")),
           (r"/m/data/?$", _import("mobile.m_main","MobileDataHandler")),
           (r"/m/about/?$", _import("mobile.m_main","MobileAboutHandler")),
           (r"/m/fav/?$", _import("mobile.m_main","MobileFavHandler")),
           (r"/m/mail/?(-?\d{1,10})?/?$", _import("mobile.m_main","MobileMailHandler")),
           (r"/m/mail/send/(\d{1,10})?/?$", _import("mobile.m_main","MobileSendMailHandler")),

           (r"/m/(\w{2,16})/?(-?\d{1,10})?/?", _import("mobile.m_main","MobilePostHandler")),
           (r"/m/(\w{2,16})/post/?", _import("mobile.m_main","MobileNewPostHandler")),
           (r"/m/(\w{2,16})/thread/(\d{1,10})/?", _import("mobile.m_main","MobileThreadHandler")),

        ]

