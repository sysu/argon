#!/usr/bin/python2
import sys
sys.path.append('../')

import chaofeng.ascii as ac
from chaofeng import LocalFrame
from chaofeng.ui import TextEditor
from libtelnet import is_chchar
from datetime import datetime
from getchar import getch
import re

class ArgoEditor(TextEditor):

    key_maps = TextEditor.key_maps
    state_bar_format = ac.save + ac.move2(24,0) + '[1;44;33m%-80s[m' + ac.restore
    
    def init(self,text=''):
        super(ArgoEditor,self).init(text)

    def refresh(self):
        super(ArgoEditor,self).refresh()
        self.state_bar()

    def state_bar(self):
        self.write(self.state_bar_format % datetime.now().ctime())

    def acceptable(self,data):
        return is_chchar(data) or (data in ac.printable)

    def message(self,text):
        self.frame.write(ac.move2(24,0)+text)

class AddPostFrame(LocalFrame):

    re_c = re.compile('[^\r\n]+')
    x_editor = ArgoEditor()
    key_maps = {
        ac.k_ctrl_c : "cancel",
        }

    def initialize(self,boardname):
        self.write(ac.clear)
        self.boardname = boardname
        self.editor = self.load(self.x_editor)
        self.editor.refresh()

    def get(self,data):
        self.editor.send(data)
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()

if __name__ == '__main__' :
    f = AddPostFrame()
    f.initialize('Test')
    f.loop()
