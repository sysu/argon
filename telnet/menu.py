# -*- coding: utf-8 -*-

import sys
sys.path.append('../')
    
from chaofeng import EndInterrupt,Timeout
from chaofeng.g import mark,static
from chaofeng.ui import Animation,ColMenu,SingleTextBox
import chaofeng.ascii as ac
from argo_frame import ArgoStatusFrame,in_history
from model import db_orm
from libtelnet import zh_format
import config

class BaseMenuFrame(ArgoStatusFrame):

    x_anim = Animation(static['active'],start_line=3)

    x_menu = None
    background = ''
    
    def initialize(self,x_menu,default=0):
        self.write(ac.clear)
        self.top_bar()
        self.anim = self.load(self.x_anim)
        self.anim.lanuch()
        self.write('\r\n')
        self.menu = self.load(x_menu,default=default,refresh=False)
        self.refresh()
        
    def refresh(self):
        self.write(ac.move2(11,0) + self.background)
        self.write(ac.move2(24,0))
        self.bottom_bar()
        self.menu.refresh()

    def get(self,data):
        self.menu.send(data)
        if data in ac.ks_finish :
            self.handle_finish()
        elif data == ac.k_ctrl_c :
            self.goto_back()
        elif data == 'h' :
            print 1
            self.show_help()
            print 2

    def handle_finish(self):
        raise NotImplementedError

    def record_x(self):
        self.record(default=self.menu.hover)

@mark('main')
class MainMenuFrame(BaseMenuFrame):

    background = static['menu/main']
    x_menus = {
        True:ColMenu(config.menu['main_guest']),
        False:ColMenu(config.menu['main']),
        }

    def initialize(self,default=0):
        super(MainMenuFrame,self).\
            initialize(self.x_menus[self.session.userid == 'guest'],default)

    @in_history
    def handle_finish(self):
        self.goto(self.menu.fetch())

    @in_history
    def show_help(self):
        self.goto('help','main')

@mark('section_menu')
class SectionMenuFrame(BaseMenuFrame):

    background = static['menu/section']
    sections = db_orm.get_all_section()
    wrapper = lambda x : ( zh_format('%d) %8s -- %s',
                                     x[0],
                                     x[1]['sectionname'],
                                     x[1]['description']),
                           ('boardlist',{'section_name':x[1]['sectionname']}),
                           x[0])
    sections_d = map(wrapper,enumerate(sections))
    sections_d[0] += ((11,5),) 

    x_menu = ColMenu(tuple(sections_d)+config.menu['section'])

    def initialize(self,default=0):
        super(SectionMenuFrame,self).initialize(self.x_menu,default)

    @in_history
    def handle_finish(self):
        res = self.menu.fetch()
        if isinstance(res,tuple) :
            self.goto(res[0],**res[1])
        else : self.goto(res)

    @in_history
    def show_help(self):
        self.goto('help','section')
