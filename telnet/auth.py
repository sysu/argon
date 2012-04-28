# -*- coding: utf-8 -*-

from chaofeng import Frame,EndInterrupt,Timeout
from chaofeng.g import mark,static
from chaofeng.ui import TextInput,Password
import chaofeng.ascii as ac

'''
实现欢迎界面，验证登陆和菜单。

可能的跳转是到相应的功能区，结束。
'''

def check_username(username):
    return True

def check_user(username,passwd):
    return True

def login(username,passwd):
    return True

@mark('welcome')
class WelcomeFrame(Frame):

    background = static['welcome'].safe_substitute(online="%(online)4s")

    hint = static['auth_prompt']
    timeout = 120
    
    def initialize(self):

        self.write(self.background % { "online" : 0 })

        p_username   = self.hint[0]
        p_username_w = self.hint[1]
        p_password   = self.hint[2]
        p_password_w = self.hint[3]

        input_name = TextInput(self)
        input_passwd = Password(self)

        while Timeout(self.timeout, EndInterrupt):
            while True:
                self.write(p_username)
                username = input_name.read()
                self.write('\r\n')
                if username == 'new' :
                    self.goto(mark['register'])
                elif username == 'guest' :
                    session['username'] = 'guest'
                    self.goto(mark['menu'],'main')
                elif not check_username(username) :
                    self.write(p_username_w)
                    continue
                self.write(p_password)
                password = input_passwd.read()
                self.write('\r\n')
                if check_user(username,password):
                    login(username,password)
                    self.goto(mark['menu'],'main')
                self.write(p_password_w)

