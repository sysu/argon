#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import Server, g, sleep, asynchronous, Frame
from chaofeng.g import mark
import login, menu,boardlist,edit,view,mail,admin,user#,,special_frame
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
        # self.goto('dd')
        # self.goto('post','Test1','3')
        pass

@mark('finish')
class FinishFrame(Frame):
    def finish(self):
        raise BadEndInterrupt

# config.data['ROOT'] = 'debug'

if __name__ == '__main__' :
    s = Server(mark[config.data['ROOT']])
    s.run()
