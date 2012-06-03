# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from argo_frame import ArgoBaseFrame
from chaofeng import EndInterrupt
from chaofeng.g import mark
import chaofeng.ascii as ac
from model import manager

@mark('bad_ending')
class BadEndingFrame(ArgoBaseFrame):

    def bad_ending(self,e):
        manager.auth.safe_logout(self.session.userid,self.session.seid)
        self.write(ac.clear + u'崩溃啦~ T.T 麻烦请报告管理员~\r\n'+ac.reset)
        self.pause()
        self.close()
