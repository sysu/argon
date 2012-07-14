# -*- coding: utf-8 -*-
# from chaofeng.g import static
from datetime import datetime
from functools import wraps

class SimpleCache:

    def __init__(self):
        self._dict = {}

    def __call__(self, key):
        def deco(self, f):
            @wraps(f)
            def wrapper(*args,**kwargs):
                if key not in self._dict:
                    self._dict[key] = f(*args,**kwargs)
                return self._dict[key]
            return wrapper
        return deco

    def clear(self):
        self._dict = {}

    def delete(self, key):
        del self._dict[key]
    
simple_cache = SimpleCache()

zh_center = lambda s,w : s.encode('gbk').center(w).decode('gbk')

def d_top_bar(l=u'',m=u'逸仙时空 Yat-Sen Channel',r=None):
    def inner(fun):
        def new_fun(self,*args,**kwargs):
            fun(self,*kwargs,**kwargs)
            self.write('123')
        return new_fun
    return inner

def zh_format(mod,*args):
    args = tuple(map(lambda x : x.encode('gbk') if isinstance(x,unicode) else x,
                     args))
    return (mod.encode('gbk') % args).decode('gbk')

def zh_format_d(mod,**kwargs):
    for key in kwargs :
        if isinstance(kwargs[key],unicode) :
            kwargs[key] = kwargs[key].encode('gbk')
    return (mod.encode('gbk') % kwargs).decode('gbk')

is_chchar = lambda data : all( c >= u'\u4e00' and c <= u'\u9fa5' for c in data)
