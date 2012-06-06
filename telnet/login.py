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
class WelcomeFrame(ArgoFrame):

    class UseridInput(TextInput):
        def acceptable(self,data):
            return data in ac.printable

    background = static['welcome'].safe_substitute(online="%(online)4s")
    timeout = 50
    prompt = static['prompt/auth']
    wrong_prompt = prompt[2]

    _userid = UseridInput(prompt=prompt[0])
    _passwd = Password(prompt=prompt[1])

    def initialize(self):
        super(WelcomeFrame,self).initialize()
        
        self.render(self.background,
                    online=manager.online.total_online())
        
        self.try_login_iter(self.timeout)
        
    def try_login_iter(self,timeout):
        
        userid_ = self.load(self._userid)
        passwd_ = self.load(self._passwd)
        
        with Timeout(timeout,EndInterrupt):
            while True :
                userid = userid_.readln()
                if userid == 'new' :
                    self.goto('register')
                elif userid == 'guest' :
                    passwd = None
                else :
                    passwd = passwd_.readln()
                # try login
                self.try_login(userid,passwd)
                
    def try_login(self,userid,passwd):
        authobj = manager.auth.login(userid,passwd,self.session.ip)
        if authobj :
            self.session.user = authobj
            if authobj.is_first_login :
                self.goto('first_login')
            else : self.goto('main')
        else:
            print authobj.content
            self.writeln(self.wrong_prompt)

@mark('first_login')
class FirstLoginFrame(ArgoBaseFrame):

    def initialize(self):
        self.write(static['first_login'] % self.session['_user']['firstlogin'])
        self.goto('main')

