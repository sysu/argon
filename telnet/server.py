# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import Server,g
from chaofeng.g import mark,static
import login,user,menu,board
import config
from model import db_orm

@mark('debug')
class LoginDebugFrame(login.WelcomeFrame):

    def hook_login(self,userobj):
        self._login(userobj,userobj['userid'])
        if userobj['numlogins'] == 1 :
            self.goto('first_login')
        self.goto('main')

    def initialize(self):
        userid = '111'
        passwd = '111111'
        user = db_orm.login(userid,passwd)
        self.hook_login(user)
        
if __name__ == '__main__' :
    s = Server(mark['debug'])
    s.run()
