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
from base_menu import BaseMenuFrame

@mark('main')
class MainMenuFrame(BaseMenuFrame):

    def initialize(self):
        menu = config.menu['main_guest' if self.session['userid'] == 'guest' else 'main']
        super(MainMenuFrame,self).initialize(
            static['menu_main'], menu)

# todo : 分类讨论区 和 其他菜单
@mark('section_menu')
class SectionMenuFrame(BaseMenuFrame):

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
        self.goto(mark['main'])

@mark('bye')
class ByeFrame(Frame):
    '''
    正常关闭的frame。
    '''
    def initialize(self):
        self.write("Bye!.\r\n")
        self.close()

