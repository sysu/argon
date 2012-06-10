# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import EndInterrupt,Timeout
from chaofeng.g import mark,static
from chaofeng.ui import Animation,ColMenu
import chaofeng.ascii as ac
from argo_frame import ArgoFrame
from model import manager
from libtelnet import zh_format
import config

class MenuFrame(ArgoFrame):

    _anim = Animation(static['active'],start_line=3)
    _menu = ColMenu()
    key_maps = ArgoFrame.key_maps.copy()
    key_maps.update({
            ac.k_ctrl_c : "goto_back",
            "h" : "show_help",
            ac.k_right:"finish",
            ac.k_left:"goto_back",
            })

    def initialize(self,name,default=0):
        super(MenuFrame,self).initialize()
        self.menu_ = self.load(self._menu)
        self.anim_ = self.load(self._anim)
        # setup
        self.name = name
        self.menu_.setup(hover=default,
                        data=self.get_menu(),
                        background=self.get_menu_background())
        self.display()

    @property
    def status(self):
        return dict(name=self.name,
                    default=self.menu_.hover)

    def display(self):
        self.cls()
        self.top_bar()
        self.anim_.lanuch()
        self.bottom_bar()
        self.write(ac.move2(11,0))
        self.menu_.display()

    def get_menu_background(self):
        return static['menu/%s' % self.name]

    def get_menu(self):
        return self._menu.tidy_data(config.menu[self.name])

    def get(self,data):
        self.menu_.send(data)
        if data in ac.ks_finish:
            self.finish()
        self.try_action(data)

    def finish(self):
        self.suspend(self.menu_.fetch())

    def show_help(self):
        self.suspend('help',page='menu_'+self.name)

@mark('main')
class MainMenuFrame(MenuFrame):

    key_maps = MenuFrame.key_maps.copy()

    def initialize(self,default=0):
        menuname = 'main_guest' if self.userid == 'guest' else 'main'
        super(MainMenuFrame,self).initialize(name=menuname, default=default)
        # self.message(u'Test OK')

    @property
    def status(self):
        return dict(default=self.menu_.hover)

    @classmethod
    def describe(cls,status):
        return u'主菜单'

@mark('sections')
class SectionMenuFrame(MenuFrame):

    key_maps = MenuFrame.key_maps.copy()
    wrapper = staticmethod(lambda x : ( zh_format('%d) %8s -- %s',
                                                  x[0],
                                                  x[1]['sectionname'],
                                                  x[1]['description']),
                                        ('boardlist',dict(sid=x[1]['sid'])),
                                        str(x[0])))
    
    def initialize(self,default=0):
        super(SectionMenuFrame,self).initialize('sections',default)

    @property
    def status(self):
        return dict(default=self.menu_.hover)

    @classmethod
    def describe(cls,status):
        return u'讨论区分类选单'

    @classmethod
    def menu_wrapper(cls,src):
        cls.sections = src
        sections_d = map(cls.wrapper,enumerate(src))
        if sections_d :
            sections_d[0] += ((11,7),)
        cls.section_menu = cls._menu.tidy_data(tuple(sections_d) + config.menu['section'])
        return cls.section_menu

    sections = None
    @classmethod
    def get_menu(cls): 
        sections = manager.section.get_all_section()
        if sections != cls.sections :
            return cls.menu_wrapper(sections)
        return cls.section_menu

    def finish(self):
        args = self.menu_.fetch()
        if isinstance(args,str):
            self.suspend(args)
        else:
            self.suspend(args[0],**args[1])
