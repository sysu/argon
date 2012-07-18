#!/usr/bin/env python 
#-*- encoding: utf8 -*-

import sys
import tornado.web

sys.path.append('..')


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
            self.remote_ip = self.request.remote_ip
        except:
            self.ref = ''
    
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

           (r"/", _import("comm.comm","HomeHandler")),

           (r"/m/?$", _import("mobile.m_main","MobileIndexHandler")),
           (r"/m/login/?$", _import("mobile.m_main","MobileLoginHandler")),
           (r"/m/logout/?$", _import("mobile.m_main","MobileLogoutHandler")),
           (r"/m/brds/?$", _import("mobile.m_main","MobileBoardHandler")),
           (r"/m/data/?$", _import("mobile.m_main","MobileDataHandler")),
           (r"/m/about/?$", _import("mobile.m_main","MobileAboutHandler")),
    
           
        ]



