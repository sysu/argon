# -*- coding: utf-8 -*-

'''
    Proxyer Server

'''

__metaclass__ = type

from chaofeng import Frame, Server, sleep, launch
import chaofeng.ascii as ac
import sys
import telnetlib
from arepr import arepr

class ProxyerFrame(Frame):

    def initialize(self, remote, charset, noprint=True, delay=0.1):
        self._tn = telnetlib.Telnet(remote)
        self.session.charset = charset
        self._delay = delay
        self._will_print=not noprint
        launch(self.refresh_auto)        
        
    def refresh(self):
        get = self.u(self._tn.read_very_eager())
        self.write(get)
        if self._will_print and get and not self.ignore(get) :
            print arepr(get)

    def refresh_auto(self):
        while True:
            sleep(self._delay)
            self.refresh()

    def get(self, char):
        if char == ac.k_ctrl_l :
            self.refresh()
        self._tn.write(self.s(char))
        if self._will_print :
            print repr(char)
        self.refresh()

    def ignore(self, data):
        return True#False#data.startswith('\x1b[3;1H')

class DefaultFrame(Frame):

    def initialize(self):
        self.raw_goto(ProxyerFrame,
                      noprint=False,
                      remote='argo.sysu.edu.cn',
                      charset='gbk')

if __name__ == '__main__' :
    s = Server(DefaultFrame, port=4999)
    s.run()
