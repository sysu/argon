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

class ArgoBaseFrame(Frame):

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

    def cls(self):
        '''
        Clear current screen.
        '''
        self.write(ac.clear)

    def format(self,string,*args,**kwargs):
        if args:
            return zh_format(string,*args)
        else:
            return zh_format_d(string,**kwargs)

    def readline(self, buf_size=20):
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

    # def render(self,string,*args):
    #     '''
    #     Write string % dict if has any key/value arguments,
    #     Or just print write to remote.
    #     '''
    #     if args :
    #         self.write( zh_format(string,*args) )
    #     else:
    #         self.write(string)

    def format_width(self,source,width):
        s = self.s(source)
        return self.u('%*s' % (width, s))

    def render(self, filename, **kwargs):
        self.write(self.render_str(filename, **kwargs))

    def packup(self):
        '''
        Packup this frame's mark and `status` .
        self.status should be a var or property.
        '''
        return (self.__mark__,self.status)

    def goto_pack(self,pack):
        '''
        Goto the frame in the pack.
        '''
        self.goto(pack[0],**pack[1])

class ArgoAuthFrame(ArgoBaseFrame):

    @property
    def charset(self):
        '''
        Overload the charset to support multiple
        charset.
        '''
        return self.session.charset

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

    # do something common

    def render_str(self, filename, **kwargs):
        t = self._jinja_env.get_template(filename)
        s = t.render(session=self.session,
                     user=self.session.user,
                     uwidth=self.format_width,
                     **kwargs)
        return s

    def suspend(self,where,**kwargs):
        '''
        Push current frame's status to history
        and goto a new frame.
        '''
        self.stack.append(self)
        self.history.append(self)
        self.goto(where,**kwargs)

    def goto_back(self):
        '''
        Go back to previous frame save in
        history.
        '''
        self.history.append(self)
        if self.stack:
            self.wakeup(self.stack.pop())

    def goto_back_nh(self):
        if self.stack:
            self.wakeup(self.stack.pop())

    def is_finish(self,data):
        return data in ac.ks_finish

    def get(self,data):
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()
        if self.is_finish(data):
            self.handle_finish()

    def restore(self):
        '''
        Handle for come back. Implemented by subclass.
        '''
        pass

    def handle_finish(self):
        pass
        # raise NotImplementedError,"What should `%s` do at the end?" % self.__mark__

    def top_bar(self):
        self.render('top')

    def bottom_bar(self):
        self.render('bottom')

    def message(self,msg):
        self.render('bottom_msg',messages=msg)
        self.pause()
        self.render('bottom')
        self.table.refresh_cursor()

class ArgoFrame(ArgoAuthFrame):

    key_maps = {
        ac.k_ctrl_c:"goto_back",
        ac.k_ctrl_be:"goto_history",
        }

    def is_gbk_zh(self,data):
        return '\x80' < data < '\xff'

    def readline(self,acceptable=ac.is_safe_char,finish=ac.ks_finish,buf_size=20, prefix=u''):
        buf = list(prefix)
        if prefix : self.write(prefix)
        while len(buf) < buf_size:
            ds = self.read_secret()
            if len(ds) == 1 and self.is_gbk_zh(ds):  ## fix_bug for sterm
                ds += self.read_secret()
            for d in self.u(ds):
                if d == ac.k_backspace :
                    if buf :
                        data = buf.pop()
                        self.write(ac.backspace * ac.srcwidth(data))
                        continue
                elif d in finish :
                    return ''.join(buf)
                elif d == ac.k_ctrl_c:
                    return False
                else:
                    if acceptable(d):
                        buf.append(d)
                        self.write(d)
        return ''.join(buf)

    def select(self,msg,options,finish=ac.ks_finish):
        if options :
            s = 0
            l = len(options) -1
            while True:
                msg(options[s])
                d = self.read_secret()
                if d == ac.k_up :
                    if s :
                        s -= 1
                elif d == ac.k_down:
                    if s<l :
                        s += 1
                elif d in '123456789':
                    s = min(l,int(d)-1)
                elif d in finish :
                    return s
                elif d == ac.k_ctrl_c:
                    return False
        return False        
                    
    def try_action(self, action):
        if action:
            getattr(self, action)()

    def goto_history(self):
        self.suspend('history')

    def send_message(self):
        pass
        
    def goto_friend(self):
        pass

    def goto_out(self):
        pass

    def watch_message(self):
        pass

    def goto_top_ten(self):
        pass

    def goto_check_user(self):
        pass

    def goto_mail(self):
        pass

@mark('undone')
class UnDoneFrame(ArgoFrame):

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
