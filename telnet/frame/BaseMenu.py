# -*- coding: utf-8 -*-

__metaclass__=type

from chaofeng import Frame,launch
from chaofeng.g import marks,mark,static
from chaofeng.ui import Animation

class BaseMenu(Frame):
    
    background = static['menu'].safe_substitute(
        pos='%(pos)10s',
        channel='逸仙时空 Yat-Sen Channel',
        pos_num='%4(pos_num)d',
        
