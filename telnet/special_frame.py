# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from libframe import BaseAuthedFrame
from view import BaseTextBoxFrame
from chaofeng import EndInterrupt
from chaofeng.g import mark
import chaofeng.ascii as ac
from model import manager

@mark('history')
class HistoryFrame(BaseTextBoxFrame):

    def initialize(self):
        self.setup(self.render_str('history', iterms=self.session.history))

    def finish(self, e=None):
        self.goto_back()
    
@mark('finish')
class FinishFrame(BaseAuthedFrame):

    def initialize(self):
        self.finish()
        self.render('undone')
        self.pause()
        if self.session['lastboardname'] :
            manager.status.exit_board(self.session['lastboardname'])
            self.session['lastboardname'] = ''
        self.close()

    def finish(self,e=None):
        try:
            manager.auth.safe_logout(self.seid)
        except AttributeError:
            pass

    def restore(self):
        self.close()

    def bad_ending(self,e):
        self.finish(e)
        self.write(ac.clear +
                   u'崩溃啦~ T.T 麻烦Bug Report~\r\n' +
                   ac.reset)

