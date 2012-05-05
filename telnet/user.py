# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import Frame,static,EndInterrupt,Timeout
from chaofeng.g import mark,is_chchar
from chaofeng.ui import TextInput,Password
from chaofeng import ascii as ac
from libtelnet import TBoard,str_top,str_bottom
from model import *
from datetime import datetime

class UsernameInput(TextInput):

    def acceptable(self,c):
        try:
            return c.isalnum() or is_chchar(c.decode('gbk')) or c == '+'
        except:
            return False

@mark('register')
class RegisterFrame(Frame):

    ban_userid = ['guest','new']

    def initialize(self):
        self.write(ac.clear+static['register_anno'])
        input_name = self.sub(UsernameInput)
        input_passwd = self.sub(Password)
        p_userid = u'请输入帐号名称 (Enter User ID, leave blank to abort): '
        p_passwd = u'请设定您的密码 (Setup Password): '
        with Timeout(150,EndInterrupt):
            while True :
                self.write(p_userid)
                userid = input_name.read_until()
                self.write('\r\n')
                if userid in self.ban_userid :
                    self.write(u'抱歉, 您不能使用该id。 请再拟。\r\n')
                elif len(userid) < 4 :
                    self.write(u'抱歉，您的id太短撩。 请再拟。\r\n')
                elif db_orm.check_user_exist(userid) :
                    self.write(u'抱歉，您的id已经被注册了。 请再拟。\r\n')
                else : break
            while True :
                self.write(p_passwd)
                passwd = input_passwd.read_until()
                self.write('\r\n')
                if len(passwd) < 6 :
                    self.write(u'密码太短了，请大于6位。\r\n')
                else : break
            db_orm.add_user(userid,passwd,{
                    'firstlogin':datetime.now(),
                    'firsthost':self.session['ip'],
                    })
            self.write(static['register_succ'])
            self.read()
            self.goto(mark['welcome'])

