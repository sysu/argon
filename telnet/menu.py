# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import EndInterrupt,Timeout
from chaofeng.g import mark
from chaofeng.ui import Animation,ColMenu
import chaofeng.ascii as ac
from argo_frame import ArgoFrame
from model import manager
from libtelnet import zh_format
import config

class MenuFrame(ArgoFrame):

    def setup(self, menu_data, menu_height, menu_start_line,
                   background, hover, anim_data):
        super(MenuFrame,self).initialize()
        self.menu = self.load(ColMenu)
        self.menu.setup(menu_data, menu_height, ac.move2(menu_start_line,0)+background, hover)
        self.anim = self.load(Animation, self.get_anim_data(), start_line=2)
        self.anim.setup()
        self.restore()

    def restore(self):
        self.cls()
        self.top_bar()
        self.bottom_bar()
        self.anim.launch()
        self.menu.restore()

    def get_anim_data(self):
        return [("1",2),("2",3)]

    def get(self,data):
        if data in ac.ks_finish:
            self.finish()
        self.menu.send_shortcuts(data)
        self.menu.try_action(config.hotkeys['menu_menu'].get(data))
        self.try_action(config.hotkeys['menu'].get(data))
        self.try_action(config.hotkeys['g'].get(data))

    def finish(self):
        raise NotImplementedError

    def right_or_finish(self):
        if not self.menu.move_right():
            self.finish()

    def left_or_finish(self):
        if not self.menu.move_left():
            self.goto_back()

@mark('main')
class MainMenuFrame(MenuFrame):

    def initialize(self):
        super(MainMenuFrame, self).initialize()
        menu_data = self.get_tidy_data()
        background = self.render_str('menu_main')
        anim_data = self.get_anim_data()
        self.setup(menu_data, 1, 11, background, 0, anim_data)

    @property
    def status(self):
        return dict(default=self.menu.hover)

    @classmethod
    def describe(cls,status):
        return u'主菜单'

    def show_help(self):
        self.suspend('help',page='main')

    # @simple_cache('main_menu_data')
    def get_tidy_data(self):
        return ColMenu.tidy_data(config.menu['main'])

    def finish(self):
        self.suspend(self.menu.fetch())

@mark('sections')
class SectionMenuFrame(MenuFrame):

    def initialize(self):
        super(SectionMenuFrame, self).initialize()
        menu_data, menu_height = self.get_tidy_data()
        background = self.render_str('menu_section')
        anim_data = self.get_anim_data()
        self.setup(menu_data, menu_height, 11, background, 0, anim_data)

    @property
    def status(self):
        return dict(default=self.menu.hover)

    @classmethod
    def describe(cls,status):
        return u'讨论区分类选单'

    def show_help(self):
        self.suspend('help',page='sections')

    @classmethod
    def wrapper_li(self, x):
        return (zh_format('%d) %8s -- %s',
                          x[0],
                          x[1]['sectionname'],
                          x[1]['description']),
                ('boardlist',dict(sid=x[1]['sid'])),
                str(x[0]))

    @classmethod
    def get_tidy_data(cls):
        sections = manager.section.get_all_section()
        menu_height = len(sections)
        sections_d = map(cls.wrapper_li, enumerate(sections))
        if sections_d :
            sections_d[0] += ((11,7),)
        li = ColMenu.tidy_data(tuple(sections_d) + config.menu['section'])
        return (li, menu_height)

    def finish(self):
        args = self.menu.fetch()
        if isinstance(args,str):
            self.suspend(args)
        else:
            self.suspend(args[0],**args[1])
