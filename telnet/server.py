#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import Server,g
from chaofeng.g import mark,static
import login,user,menu,boardlist,board,view,special_frame,editor
import config
# from model import db_orm

@mark('debug')
class LoginDebugFrame(login.WelcomeFrame):

    def initialize(self):
        # self.auth('333','123456')
        self.try_login('gcc','123456')
        # self.goto('post','Test1','3')

if __name__ == '__main__' :
    s = Server(mark[config.root])
    s.run()
