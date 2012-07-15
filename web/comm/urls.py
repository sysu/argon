#!/usr/bin/env python 

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

    def prepare(self):
        self.tpl_setting = {}
        self.tpl_setting['login'] = 0
        self.tpl_setting['msg'] = '' 

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
           (r"/m/brds/?$", _import("mobile.m_main","MobileBoardHandler")),
           (r"/m/data/?$", _import("mobile.m_main","MobileDataHandler")),
           (r"/m/about/?$", _import("mobile.m_main","MobileAboutHandler")),
    
           
        ]



