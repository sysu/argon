# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import Frame,static
from libtelnet import zh_format,zh_format_d
import chaofeng.ascii as ac
import config

from datetime import datetime
import functools

class ArgoBaseFrame(Frame):

    shortcuts = config.default_shortcuts
    
    '''
    全部类的基类。
    '''

    def u(self,data):
        return data.decode('gbk')

    def s(self,data):
        return data.encode('gbk')

    def cls(self):
        self.write(ac.clear)
        
    def render_background(self,*args,**kwargs):
        self.write(self.background % kwargs)

    def record(self,*args,**kwargs):
        self.history.append((self.__class__,args,kwargs))

    def goto_back(self):
        if self.history :
            frame,args,kwargs = self.history.pop()
            self.raw_goto(frame,*args,**kwargs)

    @property
    def history(self):
        if not hasattr(self.session,"history") :
            self.session.history = []
        return self.session.history

class ArgoStatusFrame(ArgoBaseFrame):

    top_txt = static['top']
    bottom_txt = static['bottom']

    def top_bar(self,left=u'',mid=u'逸仙时空 Yat-Sen Channel'):
        self.write( zh_format(self.top_txt,
                              left, mid, '007') )

    def bottom_bar(self,repos=False,close=False):
        if close : self.write(ac.save)
        if repos : self.write(ac.move2(24,0))
        self.write( zh_format(self.bottom_txt,
                              datetime.now().ctime(),
                              0,
                              0,
                              self.session.userid))
        if close : self.write(ac.restore)
        

    def fm(self,format_str,args):
        if isinstance(args,tuple):
            return zh_format(format_str,*args)
        elif isinstance(args,dict):
            return zh_format_d(format_str,**args)
        else :
            raise TypeError(u'No tuple or dict')

class ArgoKeymapsFrame(ArgoBaseFrame):

    def get(self,data):
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()

def in_history(f):
    @functools.wraps(f)
    def wrapper(self,*args,**kwargs):
        self.record_x()
        return f(self,*args,**kwargs)
    return wrapper

def ex_curses(f):
    @functools.wraps(f)
    def wrapper(self,*args,**kwargs):
        self.write(ac.save)
        f(self,*args,**kwargs)
        self.write(ac.restore)
    return wrapper


