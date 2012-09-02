# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from libframe import BaseAuthedFrame, BaseTextBoxFrame
from chaofeng import EndInterrupt
from chaofeng.g import mark
import chaofeng.ascii as ac
from model import manager

@mark('bad_ending')
class BadEndingFrame(BaseAuthedFrame):

    def bad_ending(self,e):
        try:
            manager.auth.safe_logout(self.userid,self.seid)
        except AttributeError:
            pass            
        self.write(ac.clear + u'崩溃啦~ T.T 麻烦到主菜单使用Bug Report报告~\r\n'+ac.reset)
        self.pause()
        self.close()

@mark('history')
class HistoryFrame(BaseTextBoxFrame):

    def get_text(self):
        return self.render_str('history',items=self.session.history)

    def finish(self, e):
        self.goto_back()

    def show_help(self):
        self.suspend('help',page='history')
    
@mark('finish')
class Finish(BaseAuthedFrame):

    def initialize(self):
        self.finish(None)
        self.render('undone')
        self.pause()
        self.close()

    def finish(self,e):
        try:
            manager.auth.safe_logout(self.seid)
        except AttributeError:
            pass            

    def bad_ending(self,e):
        self.finish(e)
        self.write(ac.clear + u'崩溃啦~ T.T 麻烦到主菜单使用Bug Report报告~\r\n[m')
        self.pause()
        self.close()
