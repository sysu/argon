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

    def goto_next(self, hover):
        raise NotImplementedError

    def goto_prev(self):
        raise NotImplementedError

    def setup(self, title, background, menu, height=None, default=0):
        self._title = title
        self._menu = self.load(ColMenu)
        self._menu.setup(menu, hover=default, height=height)
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
        self.bottom_bar()
        self.push(ac.move2(self._MENU_START_LINE, 1))
        self.push(self._menu_background)
        self._anim.launch()
        self._menu.restore()

    def _finish(self):
        hover = self._menu.fetch_num()
        self.goto_next(hover)

    def _right_or_finish(self):
        res =  self._menu.move_right()
        print res
        if not res :
        # if not self._menu.move_right() :
            self._finish()

    def _left_or_finish(self):
        if not self._menu.move_left() :
            self.goto_prev()

    def tidy_perm_menu(self, menu):
        buf = []
        for op in menu :
            if op[0] :
                if manager.perm.check_perm(self.userid, op[0]) :
                    buf.append(op[1:])
            else:
                buf.append(op[1:])
        if not buf:
            self.pause_back(u'你无权进入这个菜单！')
        return ColMenu.tidy_data(buf)

    def goto_mark_or_args(self, args):
        if isinstance(args, str):
            self.goto(args)
        else:
            self.goto(args[0], **args[1])

@mark('main')
class MainMenuFrame(BaseMenuFrame):

    _GOTO_BACK_CODE = 'g'
    DEFAULT_NAME = config.menu['__zhname__']['main']

    def goto_next(self, hover):
        self.session['menu_default']['__main__'] = hover
        self.goto_mark_or_args(self._menu.get_real(hover))

    def goto_prev(self):
        self._menu.send_shortcuts(self._GOTO_BACK_CODE)

    def initialize(self):
        title = self.DEFAULT_NAME
        background = self.render_str('menu_main')
        menu = self.tidy_perm_menu(config.menu['__main__'])
        default = self.session['menu_default'].pop('__main__', 0)
        self.setup(title, background, menu, default=default)

@mark('sections')
class SectionMenuFrame(BaseMenuFrame):

    _SECOND_COL = (11, 7)

    def initialize(self):
        title = config.menu['__zhname__']['sections']
        sections = manager.query.get_all_section()
        if not sections :
            self.cls()
            self.pause_back(u'未设置分类讨论区！')
        height = len(sections)
        section_d = map(self._wrapper_li, enumerate(sections))
        if section_d :
            section_d[0] += (self._SECOND_COL,)
        menu = ColMenu.tidy_data(section_d + config.menu['__section__'])
        background = self.render_str('menu_section')
        default = self.session['menu_default'].pop('__section__', 0)
        self.setup(title, background, menu, height=height, default=default)
    
    def _wrapper_li(self, x):
        return (self.render_str('section-li', index=x[0], **x[1]),
                ('boardlist', {"sid":x[1]['sid']}), str(x[0]))

    def goto_next(self, hover):
        if hover != self._menu.fetch_lastnum() :
            self.session['menu_default']['__section__'] = hover
        self.goto_mark_or_args(self._menu.get_real(hover))

    def goto_prev(self):
        self.goto_next(self._menu.fetch_lastnum())

@mark('menu')
class ConfigMenuFrame(BaseMenuFrame):

    def initialize(self, menuname):
        self.menuname = menuname
        title = config.menu['__zhname__'].get(menuname) or u'菜单'
        menu = self.tidy_perm_menu(config.menu[menuname])
        if ('menu_%s' % menuname) in config.all_static_file:
            background = self.render_str('menu_%s' % menuname)
        else:
            background = ''
        default = self.session['menu_default'].pop(menuname, 0)
        self.setup(title, background, menu, default=default)

    def goto_next(self, hover):
        self.session['menu_default'][self.menuname] = hover
        self.goto_mark_or_args(self._menu.get_real(hover))

    def goto_prev(self):
        self.goto_mark_or_args(
            self._menu.get_real(
                self._menu.fetch_lastnum()))

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
