# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import EndInterrupt,Timeout
from chaofeng.g import mark,static
from chaofeng.ui import TextInput,Password,DatePicker
import chaofeng.ascii as ac
from argo_frame import ArgoBaseFrame,ArgoFrame
from model import manager
# from model import UserState
from datetime import datetime
import config

class WelcomeViem(ArgoBaseFrame):

    _background = static['welcome'].safe_substitute(online='%(online)4s')

    @property
    def background(self):
        return self.format(self._background,online=manager.online.total_online())

    class UseridInput(TextInput):
        def acceptable(self,data):
            return data in ac.printable
    prompt = static['prompt/auth']
    _userid = UseridInput(prompt=prompt[0])
    _passwd = Password(prompt=prompt[1])

    def initialize(self):
        super(WelcomeViem,self).initialize()
        self.write(self.background)
        self.userid_ = self.load(self._userid)
        self.passwd_ = self.load(self._passwd)

    def read_userid(self):
        return self.userid_.readln()

    def read_passwd(self):
        return self.passwd_.readln()
        
@mark('welcome')
class WelcomeFrame(WelcomeViem):

    timeout = 50
    wrong_prompt = static['prompt/auth'][2]

    def initialize(self):
        super(WelcomeFrame,self).initialize()
        self.try_login_iter()

    def try_login_iter(self):
        with Timeout(self.timeout,EndInterrupt):
            while True :
                userid = self.read_userid()
                if userid == 'new' :
                    self.goto('register')
                elif userid == 'guest' :
                    passwd = None
                else :
                    passwd = self.read_passwd()
                # try login
                self.try_login(userid,passwd)

    def auth(self,userid,passwd):
        authobj = manager.auth.login(userid,passwd,self.session.ip)
        if authobj :
            self.session.user = authobj
            self.session.history = []
        return authobj
                
    def try_login(self,userid,passwd):
        authobj = self.auth(userid,passwd)
        if authobj :
            if authobj.is_first_login :
                self.goto('first_login')
            else : self.goto('main')
        else:
            self.writeln(self.wrong_prompt)

@mark('first_login')
class FirstLoginFrame(ArgoFrame):

    def initialize(self):
        self.write(static['first_login'] % self.session['_user']['firstlogin'])
        self.goto('main')

