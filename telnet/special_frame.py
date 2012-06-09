# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from argo_frame import ArgoFrame
from chaofeng import EndInterrupt
from chaofeng.g import mark,static
import chaofeng.ascii as ac
from model import manager

@mark('bad_ending')
class BadEndingFrame(ArgoFrame):

    def bad_ending(self,e):
        try:
            manager.auth.safe_logout(self.userid,self.seid)
        except AttributeError:
            pass            
        self.write(ac.clear + u'崩溃啦~ T.T 麻烦请报告管理员~\r\n'+ac.reset)
        self.pause()
        self.close()

@mark('finish')
class Finish(ArgoFrame):

    def initialize(self):
        self.finish(None)
        self.write(static['undone'])
        self.pause()
        self.close()

    def finish(self,e):
        try:
            manager.auth.safe_logout(self.userid,self.seid)
        except AttributeError:
            pass            

    def bad_ending(self,e):
        self.finish(e)
        self.write(ac.clear + u'崩溃啦~ T.T 麻烦请报告管理员~\r\n'+ac.reset)
        self.pause()
        self.close()
