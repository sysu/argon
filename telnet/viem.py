# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import static,mark
from chaofeng.ui import LongTextBox
from model import manager
from argo_frame import ArgoBaseFrame,in_history

import config

class ArgoTextBox(LongTextBox):

    def init(self,text,callback):
        super(ArgoTextBox,self).init(text)
        self.callback = callback

    def handle_finish(self):
        self.callback()

@mark('read_post')
class ViemFrame(ArgoBaseFrame):

    x_viem = ArgoTextBox()
    
    def initialize(self,text,next_f):
        self.viem = self.load(self.x_viem,text,self.finish)
        self.next_f = next_f
        
    def get(self,char):
        if char == ac.k_ctrl_c :
            self.finish()
        self.viem.send(char)

    def finish(self):
        self.goto(self.next_f[0],**self.next_f[1])
