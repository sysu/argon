# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import EndInterrupt,Timeout
from chaofeng.g import mark,static
from chaofeng.ui import TextInput,Password,DatePicker
import chaofeng.ascii as ac
from argo_frame import ArgoBaseFrame
from model import manager
# from model import UserState
from datetime import datetime
import config

@mark('welcome')
class WelcomeFrame(ArgoBaseFrame):

    class UseridInput(TextInput):

        def acceptable(self,data):
            return data in ac.printable

    background = static['welcome'].safe_substitute(online="%(online)4s")
    timeout = 50
    prompt = static['prompt/auth']
    wrong_prompt = prompt[2]
    
    ix_userid = UseridInput(prompt=prompt[0])
    ix_passwd = Password(prompt=prompt[1])

    def initialize(self):
        self.render_background(online=manager.online.total_online())
        i_name = self.load(self.ix_userid)
        i_passwd = self.load(self.ix_passwd)
        with Timeout(self.timeout,EndInterrupt):
            while True :
                userid = i_name.readln()
                if userid == 'new' :
                    self.goto('register')
                elif userid == 'guest' :
                    passwd = None
                else :
                    passwd = i_passwd.readln()
                # try login
                authobj = manager.auth.login(userid,passwd,self.session.ip)
                if authobj :
                    self.login(authobj)
                else :
                    self.writeln(self.wrong_prompt)

    def login(self,authobj):
        # if userid.endswith('.') :
        #     self.write(ac.clear+"Sorry, this part hasn't be done.")
        #     self.pause()
        #     raise EndInterrupt
        #     self.session.charset = 'big5'
        #     userid = userid[:-1]
        # elif userid.endswith('#') :
        #     self.pause()
        #     self.write(ac.clear+"Sorry, this part hasn't be done.")
        #     raise EndInterrupt
        #     self.session.charset = 'utf8'
        #     userid = userid[:-1]
        self.session.auth = authobj # put into session
        self.session.userid = authobj.userid  # put the userid
        if authobj.is_first_login :
            self.goto('first_login')
        else : self.goto('main')

@mark('first_login')
class FirstLoginFrame(ArgoBaseFrame):

    def initialize(self):
        self.write(static['first_login'] % self.session['_user']['firstlogin'])
        self.goto('main')

