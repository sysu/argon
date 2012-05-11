# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import EndInterrupt,Timeout
from chaofeng.g import mark,static
from chaofeng.ui import TextInput,Password,DatePicker
import chaofeng.ascii as ac
from argo_frame import ArgoBaseFrame
from model import db_orm
from datetime import datetime
import config

@mark('welcome')
class WelcomeFrame(ArgoBaseFrame):

    background = static['welcome'].safe_substitute(online="%(online)4s")
    timeout = 50
    prompt = static['auth_prompt']
    wrong_prompt = '\r\n' + prompt[2]
    
    ix_userid = TextInput(prompt='\r\n'+prompt[0])
    ix_passwd = Password(prompt='\r\n'+prompt[1])
    
    def initialize(self):
        self.render_background(online=db_orm.total_online())
        i_name = self.load(self.ix_userid)
        i_passwd = self.load(self.ix_passwd)
        with Timeout(self.timeout,EndInterrupt):
            while True :
                userid = i_name.read()
                if userid == 'new' :
                    self.goto('register')
                elif userid == 'register' :
                    self.hook_login_guest()
                else :
                    passwd = i_passwd.read()
                    user = db_orm.login(userid,passwd)
                    if user is None :
                        self.write(self.wrong_prompt)
                        continue
                    self.hook_login(user)

    def _login(self,userobj,userid):
        self.session._user = userobj # put into session
        self.session.userid = userid  # put the userid

    def hook_login(self,userobj):
        self._login(userobj,userobj['userid'])
        if userobj['numlogins'] == 1 :  # do when frist login
            self.goto('first_login')
        else : self.goto('main')

    def hook_login_guest(self):
        self._login(None,'guest')
        self.goto('main')

@mark('first_login')
class FirstLoginFrame(ArgoBaseFrame):

    def initialize(self):
        self.write(static['first_login'] % self.session['_user']['firstlogin'])
        self.goto('main')

