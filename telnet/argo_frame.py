# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import Frame
from chaofeng.g import mark
from libtelnet import zh_format,zh_format_d,zh_center
from model import manager
import chaofeng.ascii as ac
import config

from template import env

from datetime import datetime
import functools

class BaseFrame(Frame):

    '''
    全部类的基类。
    '''

    _jinja_env = env
    def render_str(self, filename, **kwargs):
        t = self._jinja_env.get_template(filename)
        s = t.render(session=self.session,
                     uwidth=self.format_width,
                     **kwargs)
        return s

    def format_str(self, f, *args):
        return f % args

    def format_width(self,source,width):
        s = self.s(source)
        return self.u('%*s' % (width, s))

    def cls(self):
        '''
        Clear current screen.
        '''
        self.write(ac.clear)

    def readline(self, buf_size=20):
        '''
        Read one line.
        '''
        buf = []
        while len(buf) < buf_size:
            ds = self.read_secret()
            for d in ds :
                if d == ac.k_backspace:
                    if buf:
                        buf.pop()
                        self.write(ac.backspace)
                        continue
                elif d in ac.ks_finish :
                    return ''.join(buf)
                elif d == ac.k_ctrl_c:
                    return False
                elif d.isalnum():
                    buf.append(d)
                    self.write(d)
        return u''.join(buf)                        

    def render(self, filename, **kwargs):
        self.write(self.render_str(filename, **kwargs))

class AuthedFrame(BaseFrame):

    def get_pipe(self):
        return self.session['_$$pipe$$']

    def set_pipe(self, value):
        print 'zzzzzzzzzzzzzz'
        self.session['_$$pipe$$'] = value

    pipe = property(get_pipe, set_pipe)

    @property
    def user(self):
        '''
        Alias for self.session.user
        '''
        return self.session.user

    @property
    def userid(self):
        '''
        Alias for self.session.user.userid
        '''
        return self.session.user.userid

    @property
    def seid(self):
        '''
        Alias for self.session.user.seid
        '''
        return self.session.user.seid

    @property
    def stack(self):
        '''
        Alias for self.session.stack, which
        used to record the goto history and
        restore.
        '''
        return self.session.stack

    @property
    def history(self):
        return self.session.history

    ##############################
    #    do something common     #
    ##############################

    # Status Control

    def suspend(self,where,**kwargs):
        '''
        Push current frame's status to history
        and goto a new frame.
        '''
        self.session.stack.append(self)
        self.session.history.append(self)
        self.goto(where,**kwargs)

    def goto_back(self):
        '''
        Go back to previous frame save in
        history.
        '''
        self.session.history.append(self)
        if self.session.stack:
            self.wakeup(self.session.stack.pop())

    def goto_back_nh(self):
        if self.stack:
            self.wakeup(self.stack.pop())

    # Additional Handle

    def restore(self):
        '''
        Handle for come back. Implemented by subclass.
        '''
        raise NotImplementedError, "How to resotre at `%s` ?" % self.__mark__

    def message(self,msg):
        raise NotImplementedError, "How to show notity in `%s` ?" % self.__mark__
    
    def get(self,data):
        raise NotImplementedError, "How to reation in `%` ?" % self.__mark__
    
    def is_finish(self,data):
        return data in ac.ks_finish

    def render_str(self, filename, **kwargs):
        t = self._jinja_env.get_template(filename)
        s = t.render(session=self.session,
                     user=self.session.user,
                     uwidth=self.format_width,
                     **kwargs)
        return s

    def do_command(self, command):
        if command :
            getattr(self, command)()

    # def top_bar(self):
    #     self.render('top')

    # def bottom_bar(self):
    #     self.render('bottom')

        # self.render('bottom_msg',messages=msg)
        # self.pause()
        # self.render('bottom')
        # self.table.refresh_cursor()

# class Frame(ArgoAuthFrame):

#     key_maps = {
#         ac.k_ctrl_c:"goto_back",
#         ac.k_ctrl_be:"goto_history",
#         }

#     def is_gbk_zh(self,data):
#         return '\x80' < data < '\xff'

#     def readline(self,acceptable=ac.is_safe_char,finish=ac.ks_finish,buf_size=20, prefix=u''):
#         buf = list(prefix)
#         if prefix : self.write(prefix)
#         while len(buf) < buf_size:
#             ds = self.read_secret()
#             if len(ds) == 1 and self.is_gbk_zh(ds):  ## fix_bug for sterm
#                 ds += self.read_secret()
#             for d in self.u(ds):
#                 if d == ac.k_backspace :
#                     if buf :
#                         data = buf.pop()
#                         self.write(ac.backspace * ac.srcwidth(data))
#                         continue
#                 elif d in finish :
#                     return ''.join(buf)
#                 elif d == ac.k_ctrl_c:
#                     return False
#                 else:
#                     if acceptable(d):
#                         buf.append(d)
#                         self.write(d)
#         return ''.join(buf)

#     def select(self,msg,options,finish=ac.ks_finish):
#         if options :
#             s = 0
#             l = len(options) -1
#             while True:
#                 msg(options[s])
#                 d = self.read_secret()
#                 if d == ac.k_up :
#                     if s :
#                         s -= 1
#                 elif d == ac.k_down:
#                     if s<l :
#                         s += 1
#                 elif d in '123456789':
#                     s = min(l,int(d)-1)
#                 elif d in finish :
#                     return s
#                 elif d == ac.k_ctrl_c:
#                     return False
#         return False        
                    
#     def try_action(self, action):
#         if action:
#             getattr(self, action)()

#     def goto_history(self):
#         self.suspend('history')

#     def send_message(self):
#         pass
        
#     def goto_friend(self):
#         pass

#     def goto_out(self):
#         pass

#     def watch_message(self):
#         pass

#     def goto_top_ten(self):
#         pass

#     def goto_check_user(self):
#         pass

#     def goto_mail(self):
#         pass

@mark('undone')
class UnDoneFrame(AuthedFrame):

    def initialize(self,*args,**kwargs):
        self.render('undone')
        self.pause()
        self.goto_back()

def load_global(var):
    def deco(f):
        @functools.wraps(f)
        def wrapper(self,name):
            if name in var :
                return var[name]
            else :
                var[name] = f(self,name)
                return var[name]
        return wrapper
    return deco
