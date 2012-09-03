#!/usr/bin/python2
# -*- coding: utf-8 -*-

from chaofeng.g import mark
from chaofeng.ui import ColMenu, Animation
import chaofeng.ascii as ac

from libframe import BaseAuthedFrame, tidy_anim
from model import manager
import config

class BaseMenuFrame(BaseAuthedFrame):

    _MENU_START_LINE = 11
    _ANIM_START_LINE = 3

    def goto_next(self, option):
        raise NotImplementedError

    def goto_prev(self):
        raise NotImplementedError

    def setup(self, title, background, menu, default=0):
        self._title = title
        self._menu = self.load(ColMenu)
        self._menu.setup(menu, hover=default)
        self._menu_background = background
        self._anim = self.load(Animation, self._get_anim(),
                               start_line=self._ANIM_START_LINE)
        self.restore()

    def get(self, char):
        if char == ac.k_finish :
            self._finish()
        self.do_command(config.shortcuts['menu'].get(char))
        self._menu.send_shortcuts(char.lower())
        self._menu.do_command(config.shortcuts['menu_ui'].get(char))

    #####################

    def place(self):
        return self._title

    def _get_anim(self):
        return tidy_anim(self.render_str('active'), 7)

    def restore(self):
        self.cls()
        self.top_bar()
        self.push(self.render_str('bottom'))
        self.push(ac.move2(self._MENU_START_LINE, 1))
        self.push(self._menu_background)
        self._anim.launch()
        self._menu.restore()

    def _finish(self):
        args = self._menu.fetch()
        self.goto_next(args)

    def _right_or_finish(self):
        if not self._menu.move_right() :
            self._finish()

    def _left_or_finish(self):
        if not self._menu.move_left() :
            self.goto_prev()

@mark('menu')
class ConfigMenuFrame(BaseMenuFrame):

    def initialize(self, menuname):
        title = config.menu['_zh_name'].get(menuname) or u'菜单'
        d_menu = config.menu[menuname]
        buf = []
        for op in d_menu :
            if op[0] :
                if manager.perm.check_perm(self.userid, op[0]) :
                    buf.append(op[1:])
            else:
                buf.append(op[1:])
        if not buf:
            self.writeln(u'你无权进入这个菜单！')
            self.pause()
            self.goto_back()
        menu = ColMenu.tidy_data(buf)
        if ('menu_%s' % menuname) in config.all_static_file:
            background = self.render_str('menu_%s' % menuname)
        else:
            background = ''
        self.setup(title, background, menu)

    def goto_prev(self):
        self.goto_back()

    def goto_next(self, option):
        if isinstance(option, str):
            self.suspend(option)
        else:
            self.suspend(option[0],**option[1])

@mark('main')
class MainMenuFrame(ConfigMenuFrame):

    def initialize(self):
        super(MainMenuFrame, self).initialize('main')

@mark('sections')
class SectionMenuFrame(BaseMenuFrame):

    _SECOND_COL = (11, 7)

    def initialize(self):
        title = config.menu['_zh_name']['sections']
        sections = manager.query.get_all_section()
        if not sections :
            self.cls()
            self.pause_back(u'未设置分类讨论区！')
        height = len(sections)
        section_d = map(self._wrapper_li, enumerate(sections))
        if section_d :
            section_d[0] += (self._SECOND_COL,)
        menu = ColMenu.tidy_data(section_d + config.menu['section'])
        background = self.render_str('menu_section')
        self.setup(title, background, menu)
    
    def _wrapper_li(self, x):
        return (self.render_str('section-li', index=x[0], **x[1]),
                ('boardlist', {"sid":x[1]['sid']}), str(x[0]))

    def goto_prev(self):
        self.goto('main')

    def goto_next(self, option):
        if isinstance(option, str):
            self.suspend(option)
        else:
            self.suspend(option[0],**option[1])

# @mark('movie')
# class PlayMovie(BaseAuthedFrame):

#     def initialize(self):
#         for i in range(10,0,-1):
#             sleep(1)
#             self.write(ac.clear + ac.move2(12, 40) + str(i))
#         self.write(ac.clear + ac.move2(12,40) + ac.blink + u'任意键继续')
#         self.pause()
#         data = tidy_anim(self.render_str('movie'), 21)
#         self.anim = self.load(Animation, data, pause=self.pause,
#                               start_line=0,  callback=self.play_done)
#         self.anim.run(playone=True)

#     def play_done(self):
#         self.pause()
#         self.goto_back()

#     def get(self, data):
#         if data in ac.k_ctrl_c:
#             self.goto_back()
