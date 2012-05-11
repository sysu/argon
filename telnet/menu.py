# -*- coding: utf-8 -*-

import sys
sys.path.append('../')
    
from chaofeng import EndInterrupt,Timeout
from chaofeng.g import mark,static
from chaofeng.ui import Animation,ColMenu
import chaofeng.ascii as ac
from argo_frame import ArgoStatusFrame
from model import db_orm
import config

class BaseMenuFrame(ArgoStatusFrame):

    x_anim = Animation(static['active'],start_line=3)

    x_menu = None
    background = ''
    
    def initialize(self,x_menu):
        self.write(ac.clear)
        self.top_bar()
        self.anim = self.load(self.x_anim)
        self.anim.lanuch()
        self.write('\r\n')
        self.write(self.background)
        self.menu = self.load(x_menu)
        self.refresh()

    def refresh(self):
        self.write(ac.move2(11,0) + self.background)
        self.write(ac.move2(24,0))
        self.bottom_bar()

    def get(self,data):
        self.menu.send(data)
        if data in ac.ks_finish :
            print self.menu.fetch()

@mark('main')
class MainMenuFrame(BaseMenuFrame):

    background = static['menu_main']
    x_menu = {
        True:ColMenu(config.menu['main_guest']),
        False:ColMenu(config.menu['main']),
        }


    def initialize(self):
        super(MainMenuFrame,self).\
            initialize(self.x_menu[self.session.userid == 'guest'])

@mark('section_menu')
class SectionMenuFrame(BaseMenuFrame):

    item_wraper = lambda x : ( zh_fromat('%d) %8s -- %s',
                                         x[0],x[1]['sectionname'],x[1]['description']),
                               ('boardlist',{'section_name':x[1]['sectionname']}),
                               x[0])

    def initialize(self):
        sections = db_orm.get_all_section()
        d = map(self.item_wraper ,enumerate(sections))
        super(SectionMenuFrame,self).initialize(static['menu_section'],tuple(d)+config.menu['section'])
