#!/usr/bin/python2
# -*- coding: utf-8 -*-

from datetime import datetime
import functools
import re

from chaofeng import Frame
from chaofeng.g import mark
import chaofeng.ascii as ac
from chaofeng.ui import TextEditor, FinitePagedTable, Animation, ColMenu,\
    NullValueError, SimpleTextBox, TableLoadNoDataError, TextEditorAreaMixIn
import config
from template import env
from model import manager
from libformat import telnet2style
import logging

logger = logging.getLogger('libframe')

class BaseFrame(Frame):

    u'''
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
        assert isinstance(source, unicode)
        s = source.encode('gbk')
        return ('%*s' % (width, s)).decode('gbk')

    def cls(self):
        u'''
        Clear current screen.
        '''
        self.write(ac.clear)

    def readline(self, buf_size=20):
        u'''
        Read one line.
        '''
        buf = []
        while True :
            ds = self.read_secret()
            for d in ds :
                if d in ac.ks_delete:
                    if buf:
                        buf.pop()
                        self.write(ac.backspace)
                        continue
                elif d in ac.ks_finish :
                    return u''.join(buf)
                elif d == ac.k_ctrl_c:
                    return False
                elif (len(buf) < buf_size) and d.isalnum():
                    buf.append(d)
                    self.write(d)
        return u''.join(buf)                        

    def render(self, filename, **kwargs):
        self.push(self.render_str(filename, **kwargs))

class BaseAuthedFrame(BaseFrame):
    
    def place(self):
        return config.mark2zhname.get(self.__mark__) or u''

    def top_bar(self):
        if self.session['lastboardname'] :
            right = u'[%s]' % self.session['lastboardname']
        else:
            right = u''
        if manager.notify.check_mail_notify(self.userid):
            tpl = 'top_notify'
        elif manager.notify.check_notice_notify(self.userid):
            tpl = 'top_notify_notice'
        else :
            tpl = 'top'
        self.render(tpl, left=self.place(), right=right)

    def bottom_bar(self):
        self.push(self.render_str('bottom'))

    # def write(self, data):
    #     super(BaseFrame, self).write(self.read())
    #     super(BaseFrame, self).write(data)

    def get_pipe(self):
        return self.session[u'_$$pipe$$']

    def set_pipe(self, value):
        self.session[u'_$$pipe$$'] = value

    def post_bug(self):
        self.suspend('post_bug')

    pipe = property(get_pipe, set_pipe)

    @property
    def user(self):
        u'''
        Alias for self.session.user
        '''
        return self.session.user

    @property
    def userid(self):
        u'''
        Alias for self.session.user.userid
        '''
        return self.session.user.userid

    @property
    def seid(self):
        u'''
        Alias for self.session.user.seid
        '''
        return self.session.user.seid

    @property
    def stack(self):
        u'''
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
        u'''
        Push current frame's status to history
        and goto a new frame.
        '''
        if self.__mark__ in self.session._stack_history :
            while self.session.stack:
                mark = self.session.stack.pop().__mark__
                self.session._stack_history.remove(mark)
                if mark == self.__mark__ :
                    break
            logger.debug('Loop in suspend. Len after clear %s',
                         len(self.session.stack))
        self.session._stack_history.add(self.__mark__)
        self.session.stack.append(self)
        # self.session.history.append(self)
        self.goto(where,**kwargs)

    def goto_back(self):
        u'''
        Go back to previous frame save in
        history.
        '''
        # self.session.history.append(self)
        if self.session.stack:
            nextframe = self.session.stack.pop()
            self.session._stack_history.remove(nextframe.__mark__)
            logger.debug('Goto back <- %20s  ---> %s', self.__mark__,
                         nextframe.__mark__)
            self.wakeup(nextframe)

    def goto_back_history(self, where):
        if where in self.session._stack_history :
            while self.session.stack:
                frame = self.session.stack.pop()
                self.session._stack_history.remove(frame.__mark__)
                if frame.__mark__ == where:
                    self.wakeup(frame)

    def goto_back_nh(self):
        if self.stack:
            self.wakeup(self.stack.pop())

    def pause_back(self, prompt):
        self.writeln(prompt)
        self.pause()
        self.goto_back()

    # Additional Handle

    def restore(self):
        u'''
        Handle for come back. Implemented by subclass.
        '''
        raise NotImplementedError, u"How to resotre at `%s` ?" % self.__mark__

    def message(self, msg):
        raise NotImplementedError, u"How to show message in `%s` ?" % self.__mark__

    def notify(self, msg):
        raise NotImplementedError, u"How to show notify in `%s` ?" % self.__mark__
    
    def get(self,data):
        raise NotImplementedError, u"How to reation in `%s` ?" % self.__mark__

    check_perm = NotImplementedError
    
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

    def readchar(self, default, acceptable=ac.isalnum, cancel='',
                 prompt=u''):
        if prompt:
            self.push(prompt)
        if default:
            self.push(default)
        while True:
            char = self.read_secret()
            if char == ac.k_ctrl_c:
                return cancel
            if char == ac.k_finish :
                return default
            if char in ac.ks_delete:
                if default:
                    self.write(ac.backspace)
                    default = ''
                continue
            if acceptable(char):
                if default :
                    self.push(ac.k_left)
                self.push(char)
                default = char

    def bottom_do(self, func, *args, **kwargs):
        self.push(ac.move2(24,1))
        self.push(ac.kill_line)
        res = func(*args, **kwargs)
        self.bottom_bar()
        return res

    def confirm(self, prompt, default=''):
        return self.readchar(default, prompt=prompt,
                             acceptable=lambda x:x == 'y' or x=='n',
                             cancel='n') == 'y'

    def safe_readline(self, prompt=u'', acceptable=ac.is_safe_char,
                      finish=ac.ks_finish,buf_size=20,  prefix=u''):
        '''
        Return the string when `finish` key recv, return False while recv a k_ctrl_c
        '''
        if prompt :
            self.write(prompt)
        if prefix :
            buf = list(prefix)
            self.write(prefix)
        else:
            buf = []
        while True:
            char = self.read_secret()
            if char in ac.ks_delete :
                if buf :
                    data = buf.pop()
                    self.write(ac.backspace * ac.srcwidth(data))
                    continue
            elif char in finish :
                return u''.join(buf)
            elif char == ac.k_ctrl_c:
                return False
            elif acceptable(char):
                if len(buf) < buf_size:
                    buf.append(char)
                    self.write(char)
        return u''.join(buf)

    # def read_lbd(self, reader):
    #     u'''
    #     Wrapper real read function.
    #     '''
    #     self.write(u''.join((ac.move2(24,1),  ac.kill_line)))
    #     res = reader()
    #     self.write(u'\r')
    #     self.bottom_bar()
    #     self._table.restore_cursor_gently()
    #     return res

    # def readline(self, acceptable=ac.is_safe_char, finish=ac.ks_finish,\
    #                  buf_size=20, prompt=u'', prefix=u''):
    #     return self.read_lbd(lambda : self.safe_readline(acceptable, finish, 
    #                                       buf_size, prompt, prefix=prefix))

    def readnum(self, prompt=u''):
        no = self.safe_readline(acceptable=lambda x:x.isdigit(),
                           buf_size=8,  prompt=prompt)
        if no :
            return int(no) - 1
        else :
            return False

    def read_with_hook(self, hook, pos, buf_size=20):
        buf = []
        while True:
            self.push(ac.move2(pos[0], pos[1]))
            ds = self.read_secret()
            ds = ds or ds[0]
            if ds == ac.k_backspace:
                if buf:
                    data = buf.pop()
                    pos[1] -= 1
                    self.write(ac.backspace)
                continue
            elif ds in ac.ks_finish:
                break
            elif ds == ac.k_ctrl_c:
                buf = False
                break
            elif len(buf) < buf_size:
                if ds.isalnum() or ds == '_' :
                    buf.append(ds)
                    self.write(ds)
                    pos[1] += 1
                    hook(u''.join(buf))
        if buf is False :
            return buf
        else:
            return u''.join(buf)                
    
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
                elif d in u'123456789':
                    s = min(l,int(d)-1)
                elif d in finish :
                    return s
                elif d == ac.k_ctrl_c:
                    return False
        return False

    def goto_history(self):
        self.suspend('history')

    def try_enter_board(self, boardname):
        if self.session['last_boardname'] != boardname :
            perm = manager.query.get_board_ability(self.userid, boardname)
            if not perm[0] :
                return False
            self.session['last_boardname'] = boardname
            self.session['last_board_perm'] =perm

    # def top_bar(self):
    #     self.render('top')

    # def bottom_bar(self):
    #     self.render('bottom')

        # self.render('bottom_msg',messages=msg)
        # self.pause()
        # self.render('bottom')
        # self.table.refresh_cursor()

def chunks(data, height):
    for i in xrange(0, len(data), height+1):
        yield (u'\r\n'.join(data[i:i+height]),int(data[height]))

def list_split(data, height):
    for i in xrange(0, len(data), height):
        yield data[i:i+height]

def tidy_anim(text, height):
    l = text.split(u'\r\n')
    return list(chunks(l, height))

def gen_quote(post):
    max_quote_line = 5
    owner = manager.userinfo.get_user(post['owner'])
    return ''.join([
            u'\n【 在 %s ( %s ) 的大作中提到: 】\n:' % (owner['userid'],
                                                   owner['nickname']),
            '\n:'.join(post['content'].split('\n')[:max_quote_line]),
            ])

def gen_quote_mail(mail):
    max_quote_line = 5
    owner = manager.userinfo.get_user(mail['fromuserid'])
    return ''.join([
            u'\n【 在 %s ( %s ) 的来信中提到: 】\n:' % (owner['userid'],
                                                        owner['nickname']),
            '\n:'.join(mail['content'].split('\n')[:max_quote_line])
            ])

def wrapper_index(data, start):
    for index in range(len(data)):
        data[index]['index'] = index + start
    return data

