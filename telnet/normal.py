# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
    
from chaofeng import Frame,EndInterrupt,Timeout
from chaofeng.g import mark,static,_w
from chaofeng.ui import TextInput,Password,Animation,ColMenu
# from lib import check_user_exist,check_user_password
from datetime import datetime
import config
import chaofeng.ascii as ac
from libtelnet import str_top,str_bottom,login_telnet
from model import db_orm

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

    def initialize(self,content,config_data):
        self.anim = self.sub(Animation,static['active'],start=3,run=True)
        self.write(ac.clear+str_top(self)+ac.move2(11,0))
        self.write(content)
        self.write(ac.move2(24,0)+str_bottom(self))
        next_f,kwargs = self.sub(ColMenu,config_data).read_until()
        self.goto(mark[next_f],**kwargs)

@mark('main_menu')
class MainMenuFrame(MenuFrame):

    def initialize(self):
        super(MainMenuFrame,self).initialize(static['menu_main'],
                                            config.menu['main'])

# todo : 分类讨论区 和 其他菜单
@mark('section_menu')
class SectionMenuFrame(MenuFrame):

    def initialize(self):
        sections = db_orm.get_all_section()
        d = map(lambda x : ( _w('%d) %8s -- %s',x[0],x[1]['sectionname']
                                ,x[1]['description']),
                             ('boardlist',{'section_name':x[1]['sectionname']}),
                             str(x[0])),enumerate(sections))
        d[0] = d[0] + ((11,6),)
        super(SectionMenuFrame,self).initialize(static['menu_section'],tuple(d)+config.menu["section"])

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

