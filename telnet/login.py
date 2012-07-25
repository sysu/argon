# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import EndInterrupt,Timeout,asynchronous
from chaofeng.g import mark
from chaofeng.ui import VisableInput,Password,DatePicker
import chaofeng.ascii as ac
from argo_frame import BaseFrame, AuthedFrame
from model import manager
from datetime import datetime
import config
from collections import deque

@mark('welcome')
class WelcomeFrame(BaseFrame):

    def initialize(self):
        print 'Connect :: %s : %s' % (self.session.ip, self.session.port)
        self.render('welcome')
        self.try_login_iter()

    def try_login_iter(self):
        passwd_reader = self.load(Password)
        with Timeout(config.max_try_login_time , EndInterrupt):
            while True :
                self.write(config.str['PROMPT_INPUT_USERID'])
                userid = self.readline()
                self.write('\r\n')
                if userid == 'new' :
                    self.goto('register')
                elif userid == 'guest':
                    self.write(config.str['PROMPT_GUEST_UNABLE_TO_USE'])
                    continue
                else:
                    passwd = passwd_reader.readln(prompt=config.str['PROMPT_INPUT_PASSWD'])
                print (userid, passwd)
                self.try_login(userid, passwd)

    @asynchronous
    def auth(self,userid,passwd):
        authobj = manager.auth.login(userid,passwd,self.session.ip)
        if authobj :
            self.session.user = authobj
            self.session.stack = deque(maxlen=config.max_stack_deep)  #!!!!
            self.session.history = deque(maxlen=config.max_history_deep)
            self.session.messages = [u'逸仙时空 argo.sysu.edu.cn']
        return authobj
                
    def try_login(self,userid,passwd):
        authobj = self.auth(userid,passwd)
        if authobj :
            self.goto('main')
        else:
            self.writeln(config.str['PROMPT_AUTH_FAILED'])

@mark('register')
class RegisterFrame(BaseFrame):

    def initialize(self):
        self.render('register')
        passwd_reader = self.load(Password, prompt=config.str['PROMPT_INPUT_PASSWD_REG'])
        with Timeout(config.max_try_register_time ,EndInterrupt) :
            while True :
                self.write(config.str["PROMPT_INPUT_USERID_REG"])
                userid = self.readline()
                self.write('\r\n')
                if self.check_userid(userid) : break
            while True :
                passwd = passwd_reader.readln()
                if self.check_passwd(passwd) : break
        self.register(userid,passwd)

    code_zh = {
        0:"PROMPT_REG_SUCC",
        1:"PROMPT_REG_CANNOT_USE",
        2:"PROMPT_REG_USERID_TOO_SHORT",
        3:"PROMPT_REG_REGISTERED",
        4:"PROMPT_REG_PASSWD_TOO_SHORT",
        }

    def check_userid(self,userid):
        s = manager.auth.is_unvail_userid(userid)
        if not s :
            self.writeln(config.str[self.code_zh[s.key]])
            return False
        return True
    
    def check_passwd(self,passwd):
        s = manager.auth.is_unvail_passwd(passwd)
        if not s :
            self.writeln(config.str[self.code_zh[s.key]])
            return False
        return True
        
    def register(self,userid,passwd):
        s = manager.auth.register(userid,passwd,firsthost=self.session.ip)
        if s :
            self.render('register_succ', userid=userid)
            self.pause()
            self.goto('welcome')
    
    def get(self,data):
        if data == ac.k_ctrl_c :
            self.write(config.str["PROMPT_CANCEL"])
            self.pause()
            self.goto('welcome')

@mark('first_login')
class FirstLoginFrame(AuthedFrame):

    def initialize(self):
        self.goto('help','index')
