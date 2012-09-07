#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

ALL_BASE_MODULE = sys.modules.keys()
import logging
# logging.basicConfig(level=10)

if __name__ == '__main__' :
    args = []
    kwargs = {}
    for a in sys.argv:
        if a.startswith('--') and '=' in a:
            k,v = a[2:].split('=')
            kwargs[k] = v
        else:
            args.append(a)
    if 'log' in kwargs:
        numeric_level = getattr(logging, kwargs['log'].upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logging.basicConfig(level=numeric_level)

from chaofeng import Server, g, sleep, asynchronous, Frame
from chaofeng.g import mark
import login, menu, boardlist, postlist,edit,view,jumper,mail,notice_box,special_frame,admin,user
import config
# from model import db_orm
from model import dbapi, manager
import datetime 
import MySQLdb

# @mark('debug')
class LoginDebugFrame(login.WelcomeFrame):

    def initialize(self):
        # self.auth('333','123456')
        # self.auth('123','123456')
        # self.goto('add_board')
        # self.goto('user_editdata')
        # self.try_login('admin','123456')
        self.try_login('admin', '123456')
        # self.try_login('test', '123456')
        # self.goto('dd')
        # self.goto('post','Test1','3')
        pass

# @mark('finish')
# class FinishFrame(Frame):
    
#     def finish(self, e=None):
#         raise BadEndInterrupt

# config.data['ROOT'] = 'debug'

manager.telnet['default_board_index'] = {}

ALL_MODULES = sys.modules.keys()

if __name__ == '__main__' :
    manager.status.clear_all()  ####################  ugly but work
    if mark.get('debug') :
        s = Server(mark['debug'])
    else:
        s = Server(mark[config.data['ROOT']])
    s.run()
