#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import Server,g
from chaofeng.g import mark,static
import login,user,menu,new_board#,post,special_frame
import config
# from model import db_orm

@mark('debug')
class LoginDebugFrame(login.WelcomeFrame):

    def initialize(self):
        self.try_login('333','123456')
        
if __name__ == '__main__' :
    s = Server(mark['debug'])
    s.run()
