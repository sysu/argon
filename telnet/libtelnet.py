# -*- coding: utf-8 -*-
from chaofeng.ui import BaseUI
from chaofeng.g import static,_s,_u
from datetime import datetime

_wCenter = lambda s,w : s.encode('gbk').center(w).decode('gbk')

class BottomBar(BaseUI):
    mod = static['bottom']
    def fetch(self):
        return _w(self.mod,(datetime.now().ctime(),0,1,self.session['username']))
    def send(self):
        return True

_top_str = _s(static['top'])
_bot_str = _s(static['bottom'])

from chaofeng.g import _s,_u

str_top = lambda f,l=u'',m=u'逸仙时空 Yat-Sen Channel' : _u(_top_str % ( _s(l),_s(m).center(40),_s(u'%s区 [%s]' % (u'pos_num',u'pos'))))

str_bottom = lambda f : _u(_bot_str % (datetime.now().ctime(),0,5,f.session['username']))
