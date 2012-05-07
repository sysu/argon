# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import Frame,EndInterrupt,Timeout
from chaofeng.g import mark,static,_w
from chaofeng.ui import TextInput,Password
import config
import chaofeng.ascii as ac
from model import db_orm
from datetime import datetime

@mark('welcome')
class WelcomeFrame(Frame):

    '''
    实现欢迎界面。
    调用model.db_orm的login验证并登陆
    成功登陆后跳转到 name=main 的menu frame。输入new转入注册，输入guest以
    guest为username登陆。
    没有最大尝试要求，但超过120s还没有登陆将会自动关闭连接。
    本页面也是全局入口，在config.root设定。
    @para none
    '''
    
    background = static['welcome'].safe_substitute(online="%(online)4s")
    hint = static['auth_prompt']
    timeout = 10

    def login_guest(self):
        self.session['_user'] = None
        self.session['userid'] = 'guest'
        self.goto(mark['main'])

    def login(self,user):
        self.session.update(user.dict)
        self.session['_user'] = user
        self.session['userid'] = user['userid']
        if user['numlogins'] == 1 :
            self.goto(mark['first_login'])
        self.goto(mark['main'])
    
    def initialize(self):

        # todo : $online
        self.write(self.background % { "online" : 0 })

        p_username   =  self.hint[0]
        p_password   =  '\r\n'+self.hint[1]
        p_wrong =  '\r\n'+self.hint[2]+'\r\n'

        input_name = self.sub(TextInput)
        input_passwd = self.sub(Password)

        with Timeout(self.timeout, EndInterrupt):
            while True:
                self.write(p_username)
                username = input_name.read_until()
                if username == 'new' :
                    self.goto(mark['register'])
                elif username == 'guest' :
                    self.login_guest()
                else :
                    self.write(p_password)
                    password = input_passwd.read_until()
                    user = db_orm.login(username,password,self.session['ip'])  # here call the modellogin
                    if not user :
                        self.write(p_wrong)
                        input_name.clear()
                        continue
                    user.init_user_info()
                    self.login(user)

@mark('first_login')
class FirstLoginFrame(Frame):

    def initialize(self):
        self.write(static['first_login'] % self.session['_user']['firstlogin'])
        self.goto(mark['main'])

