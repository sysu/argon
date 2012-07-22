# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import EndInterrupt,Timeout,sleep
from chaofeng.g import mark
from chaofeng.ui import Animation,ColMenu
import chaofeng.ascii as ac
from argo_frame import ArgoFrame
from model import manager
from libtelnet import zh_format
import config

def chunks(data, height):
    for i in xrange(0, len(data), height+1):
        yield ('\r\n'.join(data[i:i+height]),int(data[height]))

def tidy_anim(text, height):
    l = text.split('\r\n')
    return list(chunks(l, height))

@mark('movie')
class PlayMovie(ArgoFrame):

    def initialize(self):
        for i in range(10,0,-1):
            sleep(1)
            self.write(ac.clear + ac.move2(12, 40) + str(i))
        self.write(ac.clear + ac.move2(12,40) + ac.blink + u'任意键继续')
        self.pause()
        anim = tidy_anim(self.render_str('movie'), 21)
        self.setup(anim)
        self.start()
    
    def setup(self, data):
        self.cls()
        self.anim = self.load(Animation, data, start_line=1)
        self.anim.setup(playone=True)

    def start(self):
        self.anim.launch()

    def play_done(self):
        self.pause()
        self.goto_back()

class MenuFrame(ArgoFrame):

    def setup(self, menu_data, menu_height, menu_start_line,
                   background, hover, anim_data):
        super(MenuFrame,self).initialize()
        self.menu = self.load(ColMenu)
        self.menu.setup(menu_data, menu_height, ac.move2(menu_start_line,0)+background, hover)
        data =  self.get_anim_data()
        self.anim = self.load(Animation, data, start_line=3)
        self.restore()

    def restore(self):
        self.cls()
        self.top_bar()
        self.bottom_bar()
        self.anim.launch()
        self.menu.restore()

    def get_anim_data(self):
        # txt = self.render_str('active').split('\r\n')
        # anim = list(chunks(txt,7))
        # return anim
        return tidy_anim(self.render_str('active'), 7)

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
        self.setup(menu_data, False, 11, background, 0, anim_data)

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
