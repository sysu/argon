#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import Server,g
from chaofeng.g import mark
import login, menu,boardlist#,user,menu,boardlist,board,view,special_frame,editor
import config
# from model import db_orm

@mark('debug')
class LoginDebugFrame(login.WelcomeFrame):

    def initialize(self):
        # self.auth('333','123456')
        self.try_login('333','555555')
        # self.goto('post','Test1','3')

config.root = 'debug'

if __name__ == '__main__' :
    s = Server(mark[config.root])
    s.run()
