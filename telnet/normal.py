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

        input_name = TextInput(self)
        input_passwd = Password(self)

        while Timeout(self.timeout, EndInterrupt):
            while True:
                self.write(p_username)
                username = input_name.read()
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
                password = input_passwd.read()
                if check_user_password(username,password):
                    self.session['username'] = username
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

        #todo : get pos info
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
                "online_friend":0, #todo : online_friend
                "username":self.session['username']})

        next_f,kwargs = ColMenu(self,config.menu[name]).read()
        self.goto(mark[next_f],**kwargs)

@mark('unf')
class UnfinishFrame(Frame):
    '''
    未实现的frame。
    '''
    def initialize(self,*kwargs):
        self.write("This part isn't finish.")
        self.close()

@mark('bye')
class ByeFrame(Frame):
    '''
    正常关闭的frame。
    '''
    def initialize(self):
        self.write("Bye!.\r\n")
        self.close()

