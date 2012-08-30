#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

ALL_BASE_MODULE = sys.modules.keys()

from chaofeng import Server, g, sleep, asynchronous, Frame
from chaofeng.g import mark
import login, menu,boardlist,edit,view,mail,game,special_frame ,admin,user
import config
# from model import db_orm
from model import dbapi
import datetime 
import MySQLdb

@mark('debug')
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

@mark('finish')
class FinishFrame(Frame):
    
    def finish(self, e=None):
        raise BadEndInterrupt

#config.data['ROOT'] = 'debug'

ALL_MODULES = sys.modules.keys()

if __name__ == '__main__' :
    s = Server(mark[config.data['ROOT']])
    s.run()
