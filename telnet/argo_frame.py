# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import Frame,static
from chaofeng.g import mark
from libtelnet import zh_format,zh_format_d,zh_center
from model import manager
import chaofeng.ascii as ac
import config

from datetime import datetime
import functools

class ArgoBaseFrame(Frame):

    '''
    全部类的基类。
    '''

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

    def render(self,string,*args):
        '''
        Write string % dict if has any key/value arguments,
        Or just print write to remote.
        '''
        if args :
            self.write( zh_format(string,*args) )
        else:
            self.write(string)

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

    def describe(self,status):
        return u"一个普通的画面"

    def getdesc(self,status):
        return mark[status[0]].describe(status[1])

class ArgoAuthFrame(ArgoBaseFrame):

    @property
    def charset(self):
        '''
        Overload the charset to support multiple
        charset.
        '''
        return self.session.charset

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

    def suspend(self,where,**kwargs):
        '''
        Push current frame's status to history
        and goto a new frame.
        '''
        p = self.packup()
        self.stack.append(p)
        self.history.append(self.packup())
        self.goto(where,**kwargs)

    def goto_back(self):
        '''
        Go back to previous frame save in
        history.
        '''
        self.history.append(self.packup())
        if self.stack:
            self.goto_pack(self.stack.pop())

    def goto_back_nh(self):
        if self.stack:
            self.goto_pack(self.stack.pop())

    def is_finish(self,data):
        return data in ac.ks_finish

    def get(self,data):
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()
        if self.is_finish(data):
            self.handle_finish()

    def handle_finish(self):
        pass
        # raise NotImplementedError,"What should `%s` do at the end?" % self.__mark__

    top_txt = static['top']
    def top_bar(self,left=u'',mid=u'逸仙时空 Yat-Sen Channel',right=None):
        if right is None :
            try:
                right = self.session.lastboard
            except AttributeError:
                right = ''
        self.write( zh_format(self.top_txt,
                              left, zh_center(mid,40), right) )

    bottom_txt = ac.move2(24,1) + static['bottom_bar/common'] + ac.reset
    def bottom_bar(self):
        self.write(zh_format(self.bottom_txt,
                             datetime.now().ctime(),
                             manager.online.total_online(),
                             self.userid))

    message_txt = ac.move2(24,1) + static['bottom_bar/common_msg'] + ac.reset
    def message(self,msg):
        self.write(zh_format(self.message_txt, datetime.now().ctime(),
                             manager.online.total_online(), self.userid, msg[:20]))

class ArgoFrame(ArgoAuthFrame):

    key_maps = {
        ac.k_ctrl_c:"goto_back",
        ac.k_ctrl_be:"goto_history",
        }

    def readline(self,acceptable=ac.is_safe_char,finish=ac.ks_finish,buf_size=20):
        buf = []
        while len(buf) < buf_size:
            ds = self.read_secret()
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
                elif acceptable(d):
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
                if d == ac.k_up and s :
                    s -= 1
                elif d == ac.k_down and s<l :
                    s += 1
                elif d in finish :
                    return s
                else:
                    return False
        return False        
                    
    def try_action(self,data):
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()

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

    background = static['undone']
    
    def initialize(self,*args,**kwargs):
        self.write(self.background)
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
