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
from libtelnet import str_top,str_bottom,login_telnet

'''
实现欢迎界面，验证登陆和菜单。

可能的跳转是到相应的功能区，结束。
'''

@mark('welcome')
class WelcomeFrame(Frame):
    '''
    实现欢迎界面。

    调用lib/check_user_exit和lib\check_user_password进行验证。

    成功登陆后跳转到 name=main 的menu frame。输入new转入注册，输入guest以
    guest为username登陆。

    没有最大尝试要求，但超过120s还没有登陆将会自动关闭连接。

    本页面也是全局入口，在config.root设定。
    
    @para none
    '''

    background = static['welcome'].safe_substitute(online="%(online)4s")

    hint = static['auth_prompt']
    timeout = 120
    
    def initialize(self):

        # todo : $online
        self.write(self.background % { "online" : 0 })

        p_username   =  self.hint[0]
        p_username_w =  '\r\n'+self.hint[1]+'\r\n'
        p_password   =  '\r\n'+self.hint[2]
        p_password_w =  '\r\n'+self.hint[3]+'\r\n'

        input_name = self.sub(TextInput)
        input_passwd = self.sub(Password)

        while Timeout(self.timeout, EndInterrupt):
            while True:
                self.write(p_username)
                username = input_name.read_until()
                if username == 'new' :
                    #todo : register
                    self.goto(mark['register'])
                elif username == 'guest' :
                    #todo : login as guest
                    session['username'] = 'guest'
                    self.goto(mark['menu'])
                elif not check_user_exist(username) :
                    self.write(p_username_w)
                    continue
                self.write(p_password)
                password = input_passwd.read_until()
                if check_user_password(username,password):
                    login_telnet(self,username)
                    #todo : login hook
                    self.goto(mark['menu'])
                self.write(p_password_w)

@mark('menu')
class MenuFrame(Frame):
    '''
    浏览全部菜单的类。菜单的名字通过name在调用initialize时传入。
    
    将会以session['pos']和session['board_num']和session['boardname']作为
    当前所在的位置，讨论区的编号，讨论区的名字输出。

    电子公告版取active.ani作为内容。

    online和online_friend用于输出在线人数（未实现）。

    利用config中的menu[name]来设置菜单(ColMenu类),eg :
       ( (fram_mark,goto_kwargs),shortcuts, [ (pos_l,pos_r) ] )
       ...
    其中frame_mark表示将会跳转到mark[frame_mark]，goto_kwargs是跳转时的
    参数，是一个字典，shortcuts是快捷键。如果需要，可以加入 (pos_l,pos_r)
    表示这个菜单项的位置，如果不加，默认在上一项的下面。

    keypoint:
         static['active'] 为电子公告板的内容
         config.menu[name] 为该菜单的相关设定
         static['menu_'+name] 为该菜单显示的内容（包括背景和菜单字）

    @para name : 表示这个菜单的名字，将会加载与名字相关的内容。应该为
                 英文
    '''

    def initialize(self,name="main"):
        self.anim = self.sub(Animation,static['active'],start=3,run=True)
        self.write(ac.clear+str_top(self)+ac.move2(11,0))
        self.write(static['menu_'+name])
        self.write(ac.move2(24,0)+str_bottom(self))
        next_f,kwargs = self.sub(ColMenu,config.menu[name]).read_until()
        self.goto(mark[next_f],**kwargs)

@mark('undone')
class UnfinishFrame(Frame):
    '''
    未实现的frame。
    '''
    def initialize(self,*kwargs):
        self.write(ac.clear+"This part isn't finish.")
        self.read()
        self.goto(mark['menu'],name="main")

@mark('bye')
class ByeFrame(Frame):
    '''
    正常关闭的frame。
    '''
    def initialize(self):
        self.write("Bye!.\r\n")
        self.close()

