# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
    
from chaofeng import Frame,EndInterrupt,Timeout
from chaofeng.g import mark,static
from chaofeng.ui import TextInput,Password,Animation,ColMenu
from lib import check_user_exist,check_user_password
from datetime import datetime
import config
import chaofeng.ascii as ac

'''
实现欢迎界面，验证登陆和菜单。

可能的跳转是到相应的功能区，结束。
'''

@mark('welcome')
class WelcomeFrame(Frame):

    background = static['welcome'].safe_substitute(online="%(online)4s")

    hint = static['auth_prompt']
    timeout = 120
    
    def initialize(self):

        self.write(self.background % { "online" : 0 })

        p_username   =  self.hint[0]
        p_username_w =  '\r\n'+self.hint[1]+'\r\n'
        p_password   =  '\r\n'+self.hint[2]
        p_password_w =  '\r\n'+self.hint[3]+'\r\n'

        input_name = TextInput(self)
        input_passwd = Password(self)

        while Timeout(self.timeout, EndInterrupt):
            while True:
                self.write(p_username)
                username = input_name.read()
                if username == 'new' :
                    self.goto(mark['register'])
                elif username == 'guest' :
                    session['username'] = 'guest'
                    self.goto(mark['menu'])
                elif not check_user_exist(username) :
                    self.write(p_username_w)
                    continue
                self.write(p_password)
                password = input_passwd.read()
                if check_user_password(username,password):
                    self.session['username'] = username
                    self.goto(mark['menu'])
                self.write(p_password_w)

@mark('menu')
class MenuFrame(Frame):

    info_format = "%s区 [%s]"
    
    background = static['menu'].safe_substitute(
        pos="%(pos)8s",
        pos_info="%(pos_info)10s",
        board="%(board)s",
        content="%(content)s",
        time="%(time)24s",
        online="%(online)4d",
        online_friend="%(online_friend)4d",
        username="%(username)10s")

    def initialize(self,name="main"):
        self.anim = Animation(self,static['active'],start=3)
        self.anim.run_bg()

        pos = self.session.get('pos')
        if not pos :
            pos = ''
            pos_info = ''
        else:
            pos_info = self.info_format % (self.session['pos_num'],
                                           self.session['boardname'])
            
        self.write(self.background % {
                "pos": pos,
                "pos_info": pos_info,
                "board":self.anim.fetch()[0],
                "content":static['menu_'+name],
                "time":datetime.now().ctime(),
                "online":0,
                "online_friend":0,
                "username":self.session['username']})

        next_f,kwargs = ColMenu(self,config.menu[name]).read()
        self.goto(mark[next_f],**kwargs)

@mark('unf')
class UnfinishFrame(Frame):

    def initialize(self):
        self.write("This part isn't finish.")
        self.close()

@mark('bye')
class ByeFrame(Frame):

    def initialize(self):
        self.write("Bye!.\r\n")
        self.close()

