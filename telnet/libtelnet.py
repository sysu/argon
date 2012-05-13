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

def d_top_bar(l=u'',m=u'逸仙时空 Yat-Sen Channel',r=None):
    def inner(fun):
        def new_fun(self,*args,**kwargs):
            fun(self,*kwargs,**kwargs)
            self.write('123')
        return new_fun
    return inner

def login_telnet(frame,username):
    user = User(username)
    user.init_user_info()
    frame.session.update(user.dict)
    frame.session['_user'] = user
    frame.session['username'] = username
    return user

def zh_format(mod,*args):
    args = tuple(map(lambda x : x.encode('gbk') if isinstance(x,unicode) else x,
                     args))
    return (mod.encode('gbk') % args).decode('gbk')

def zh_format_d(mod,**kwargs):
    for key in kwargs :
        if isinstance(kwargs[key],unicode) :
            kwargs[key] = kwargs[key].encode('gbk')
    print 'c'*20
    print mod
    print kwargs
    print 'd'*20
    return (mod.encode('gbk') % kwargs).decode('gbk')
