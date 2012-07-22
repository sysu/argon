# -*- coding: utf-8 -*-

__metaclass__ = type

import sys
sys.path.append('../')

from chaofeng.g import mark
from chaofeng.ui import Animation,ColMenu
import chaofeng.ascii as ac
from argo_frame import AuthedFrame
from model import manager
import config

class BaseMenuFrame(AuthedFrame):

    menu_start_line = 11
    anim_start_line = 3

    def initialize(self):
        super(BaseMenuFrame, self).initialize()
        self.menu = self.load(ColMenu)
        menu,height,background = self.load_all()
        self.menu.setup(menu,
                        height, 
                        ''.join((ac.move2(self.menu_start_line, 1) ,
                                 background)))
        anim_data = self.get_anim_data()
        self.anim = self.load(Animation, anim_data,
                              start_line=self.anim_start_line)
        self.restore()

    def top_bar(self):
        self.render('top')

    def bottom_bar(self):
        self.render('bottom')

    def message(self, msg):
        self.write(ac.move2(0, 1))
        self.render('top_msg',messages=msg)
        self.menu.refresh_cursor_gently()

    def restore(self):
        self.cls()
        self.top_bar()
        self.bottom_bar()
        self.anim.launch()
        self.menu.restore()

    def get_anim_data(self):
        return tidy_anim(self.render_str('active'), 7)

    def get(self,data):
        if data in ac.ks_finish:
            self.finish()
        self.menu.send_shortcuts(data)
        self.menu.do_command(config.hotkeys['menu_menu'].get(data))
        self.do_command(config.hotkeys['menu'].get(data))
        self.do_command(config.hotkeys['g'].get(data))

    def right_or_finish(self):
        if not self.menu.move_right():
            self.finish()

    def left_or_finish(self):
        if not self.menu.move_left():
            self.goto_back()

    def finish(self):
        args = self.menu.fetch()
        if isinstance(args,str):
            self.suspend(args)
        else:
            self.suspend(args[0],**args[1])

    def load_all(self):
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
        return ColMenu.tidy_data(config.menu[self.menuname])

@mark('main')
class MainMenuFrame(BaseMenuFrame):

    def load_all(self):
        height = None
        menu = ColMenu.tidy_data(config.menu['main'])
        background = self.render_str('menu_main')
        return (menu, height, background)

    # def show_help(self):
    #     self.suspend('help',page='main')

@mark('sections')
class SectionMenuFrame(BaseMenuFrame):

    second_start_point = (11,7)

    def load_all(self):
        sections = manager.section.get_all_section()
        height = len(sections)
        sections_d = map(self.wrapper_li, enumerate(sections))
        if sections_d :
            sections_d += (self.second_start_point, )
        menu = ColMenu.tidy_data(tuple(sections_d) + config.menu['section'])
        background = self.render_str('menu_section')
        return (menu, height, background)

    def wrapper_li(self, x):
        return (self.render_str('section-li', index=x[0], **x[1]),
                str(x[0]))

    # def show_help(self):
    #     self.suspend('help',page='sections')


def chunks(data, height):
    for i in xrange(0, len(data), height+1):
        yield ('\r\n'.join(data[i:i+height]),int(data[height]))

def tidy_anim(text, height):
    l = text.split('\r\n')
    return list(chunks(l, height))

from chaofeng import sleep
# @mark('movie')
# class PlayMovie(ArgoFrame):

#     def initialize(self):
#         for i in range(10,0,-1):
#             sleep(1)
#             self.write(ac.clear + ac.move2(12, 40) + str(i))
#         self.write(ac.clear + ac.move2(12,40) + ac.blink + u'任意键继续')
#         self.pause()
#         anim = tidy_anim(self.render_str('movie'), 21)
#         self.setup(anim)
#         self.start()
    
#     def setup(self, data):
#         self.cls()
#         self.anim = self.load(Animation, data, start_line=1)
#         self.anim.setup(playone=True)

#     def start(self):
#         self.anim.launch()

#     def play_done(self):
#         self.pause()
#         self.goto_back()
