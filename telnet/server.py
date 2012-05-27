#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import Server,g
from chaofeng.g import mark,static
import login,user#,menu,board,post,special_frame
import config
# from model import db_orm

@mark('debug')
class LoginDebugFrame(login.WelcomeFrame):

    def initialize(self):
        self.session.charset = 'gbk'
        self.handle_login('111','111111')
        
if __name__ == '__main__' :
    s = Server(mark[config.root])
    s.run()
