# -*- coding: utf-8 -*-
from chaofeng.g import static,_s,_u
from datetime import datetime

_wCenter = lambda s,w : s.encode('gbk').center(w).decode('gbk')

_top_str = _s(static['top'])
_bot_str = _s(static['bottom'])

from chaofeng.g import _s,_u
from model import User

str_top = lambda f,l=u'',m=u'逸仙时空 Yat-Sen Channel' : _u(_top_str % ( _s(l),_s(m).center(40),_s(u'%s区 [%s]' % (u'pos_num',u'pos'))))

str_bottom = lambda f : _u(_bot_str % (datetime.now().ctime(),0,5,_s(f.session['userid'])))

class TBoard:
    '''
    对Board的简单包装，使其更适于telnet使用。
    TBoard[key] 没有任何意义，只是单纯地表示Board的第key张帖子。
    '''
    def __init__(self,boardobj,limit=20):
        self.body = boardobj
        self.start = -limit
        self.limit = limit
        self.res = []
        self.len = int(self.body.get_total())

    def __getitem__(self,key):
        pos = key - self.start
        if pos >= self.limit or pos < 0 :
            pos = key % self.limit
            self.start = key - pos
            self.len = int(self.body.get_total())
            self.res = self.body.get_post(self.start,
                                               self.start + self.limit)
        return self.res[pos]

    def __len__(self):
        return self.len

def login_telnet(frame,username):
    user = User(username)
    user.init_user_info()
    frame.session.update(user.dict)
    frame.session['_user'] = user
    frame.session['username'] = username
    return user

