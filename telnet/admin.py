# -*- coding: utf-8 -*-

__metaclass__ = type

import sys
sys.path.append('../')

from chaofeng.g import mark
from chaofeng.ui import Animation,ColMenu
import chaofeng.ascii as ac
from argo_frame import AuthedFrame
from model import manager
from menu import SelectFrame
import config
import codecs

@mark('sys_edit_menu_background')
class EditMenuBackgroundFrame(SelectFrame):

    def initialize(self):
        real = config.menu_background.keys()
        text = config.menu_background.values()
        super(EditMenuBackgroundFrame, self).initialize(real, text, (3,10))

    def finish(self):
        hover = self.menu.fetch()
        self.suspend('edit_text', filename=hover, callback=self.save_to_file,
                     text=self.get_background(hover))

    def get_background(self, hover):
        with codecs.open('static/%s' % hover, 'r', 'utf8') as f:
            buf = f.readlines()
            text = u'\r\n'.join(buf)
        return text

    def save_to_file(self, text):
        print text

@mark('menu')
class NewBoardFrame(AuthedFrame):
    pass
    # def initialize(self):
    #     form = self.load(Form, buf, [
    #             self.load(

class TeamSelecter(BaseUI):

    def init(self, teams):
        self.frame.cls()
        self.
