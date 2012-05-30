# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import EndInterrupt,Timeout
from chaofeng.g import mark,static
from chaofeng.ui import Animation,ColMenu
import chaofeng.ascii as ac
from argo_frame import ArgoStatusFrame,in_history
from model import manager
from libtelnet import zh_format
import config

class MenuFrame(ArgoStatusFrame):

    x_anim = Animation(static['active'],start_line=3)
    x_menu = ColMenu()
    menus = {}
    key_maps = {
        ac.k_ctrl_c : "goto_back",
        "h" : "show_help",
        }

    def background(self):
        self.cls()
        self.top_bar()
        self.anim = self.load(self.x_anim)
        self.anim.lanuch()
        self.bottom_bar(repos=True)
        self.write(ac.move2(11,0))
        self.menu.refresh()

    def get_menu(self):
        menuname = self.menuname
        if menuname in self.menus :
            return self.menus[menuname]
        else :
            nm = self.x_menu.copy()
            nm.setup(config.menu[menuname],background=static['menu/%s' % menuname])
            self.menus[menuname] = nm
            return nm

    def initialize(self,menuname,default=0):
        self.menuname = menuname
        p_menu = self.get_menu()
        self.menu = self.load(p_menu,default=default,refresh=False)
        self.background()
        
    def get(self,data):
        self.menu.send(data)
        if data in ac.ks_finish:
            self.finish()
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()

    def handle_record(self):
        self.record(default=self.menu.hover)

    @in_history
    def finish(self):
        self.goto(self.menu.fetch())

    @in_history
    def show_help(self):
        self.goto('help','menu_'+self.menuname)

@mark('main')
class MainMenuFrame(MenuFrame):

    key_maps = MenuFrame.key_maps.copy()

    def initialize(self,default=0):
        menuname = 'main_guest' if self.session.auth.userid == 'guest' else 'main'
        super(MainMenuFrame,self).initialize(menuname, default)

@mark('section_menu')
class SectionMenuFrame(MenuFrame):

    key_maps = MenuFrame.key_maps.copy()
    sections = None
    wrapper = staticmethod(lambda x : ( zh_format('%d) %8s -- %s',
                                                  x[0],
                                                  x[1]['sectionname'],
                                                  x[1]['description']),
                                        ('boardlist',dict(sid=x[1]['sid'])),
                                        x[0]))
    p_menu = ColMenu()
    
    def initialize(self,default=0):
        super(SectionMenuFrame,self).initialize('section',default)

    @classmethod
    def refresh_menu(cls,sections):
        cls.sections = sections
        sections_d = map(cls.wrapper,enumerate(sections))
        if sections_d :
            sections_d[0] += ((11,7),)
        cls.p_menu.setup(tuple(sections_d) + config.menu['section'],
                         background=static['menu/section'])

    @classmethod
    def get_menu(cls): 
        sections = manager.section.get_all_section()
        if sections != cls.sections :
            cls.refresh_menu(sections)
        return cls.p_menu

    @in_history
    def finish(self):
        args = self.menu.fetch()
        if isinstance(args,str):
            self.goto(args)
        else:
            self.goto(args[0],**args[1])
