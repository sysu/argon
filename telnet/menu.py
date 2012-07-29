#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng.g import mark
from chaofeng.ui import Animation,ColMenu
import chaofeng.ascii as ac
from libframe import BaseAuthedFrame, BaseSelectFrame, BaseMenuFrame
from model import manager
import config

class SelectFrame(BaseSelectFrame):

    u'''
    options = ( value1, value2, ...)
    text = (text1, text2, ...)
    spos = (startx, starty)
    '''

    menu_start_line = 2
    
    def initialize(self, options, text, spos , height=None, background=''):
        self._options = options
        self._text = text
        self._sx, self._sy = spos
        self._height = height
        self._background = background
        super(SelectFrame, self).initialize()

    def load_all(self):
        l = len(self._options)
        pos = [ (self._sx+i, self._sy) for i in range(l) ]
        keys = dict( (str(i+1),i) for i in range(l) )
        return (self._options, pos, keys, self._text), self._height, self._background

    def finish(self):
        raise NotImplementedError

@mark('menu')
class NormalMenuFrame(BaseMenuFrame):

    def initialize(self, menuname):
        self.set_menu(menuname)
        super(NormalMenuFrame, self).initialize()

    def set_menu(self, menuname):
        if menuname in config.menu:
            self.menuname = menuname
        else:
            self.message(config.str['NO_SUCH_MENU'])
            self.pause()
            self.goto_back()

    def load_all(self):
        height = None
        menu = ColMenu.tidy_data(config.menu[self.menuname])
        if self.menuname in config.background_file:
            background = self.render_str('menu_%s' % self.menuname)
        else:
            background = ''
        return (menu, height, background)

@mark('main')
class MainMenuFrame(BaseMenuFrame):

    def load_all(self):
        height = None
        print config.menu['main'] + config.menu['main_admin']
        menu = ColMenu.tidy_data(config.menu['main'] + config.menu['main_admin'])
        background = self.render_str('menu_main')
        return (menu, height, background)

    # def show_help(self):
    #     self.suspend('help',page='main')

@mark('sections')
class SectionMenuFrame(BaseMenuFrame):

    second_start_point = (11,7)

    def load_all(self):
        sections = manager.query.get_all_section()
        if not sections:
            self.cls()
            self.writeln(u'未设置分类讨论区！')
            self.pause()
            self.goto_back()            
        height = len(sections)
        sections_d = map(self.wrapper_li, enumerate(sections))
        if sections_d :
            sections_d[0] += (self.second_start_point,)
        menu = ColMenu.tidy_data(sections_d + config.menu['section'])
        background = self.render_str('menu_section')
        return (menu, height, background)

    def wrapper_li(self, x):
        return (self.render_str('section-li', index=x[0], **x[1]),
                ('boardlist', {"sid":x[1]['sid']}),
                str(x[0]))

    # def show_help(self):
    #     self.suspend('help',page='sections')


from chaofeng import sleep
from libframe import tidy_anim

@mark('movie')
class PlayMovie(BaseAuthedFrame):

    def initialize(self):
        for i in range(10,0,-1):
            sleep(1)
            self.write(ac.clear + ac.move2(12, 40) + str(i))
        self.write(ac.clear + ac.move2(12,40) + ac.blink + u'任意键继续')
        self.pause()
        data = tidy_anim(self.render_str('movie'), 21)
        self.anim = self.load(Animation, data, pause=self.pause,
                              start_line=0,  callback=self.play_done)
        self.anim.run(playone=True)

    def play_done(self):
        self.pause()
        self.goto_back()
