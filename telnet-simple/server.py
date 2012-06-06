#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import Server,g
from chaofeng.g import mark,static
from chaofeng.ui import zhTextInput
import chaofeng.ascii as ac

import config,traceback
from model import manager
from argo_frame import *
import functools
import string

DEBUG = True

def nothing(self):pass

def debug_if_debug(f):
    global DEBUG
    if DEBUG:
        @functools.wraps(f)
        def wrapper(self):
            if not hasattr(self.__class__,'__debuged__') :
                self.__class__.__debuged__ = True
                self.debug()
            f(self)
        return wrapper
    else:
        return f

def need_super(f):
    @functools.wraps(f)
    def warpper(self,*args):
        if self.is_super :
            f(self,*args)
        else:
            raise ActionInterrupt('You have not this perm')

class ActionInterrupt(Exception):

    def __init__(self,info,is_error=False,is_debug=True):
        self.info = info
        self.is_error = is_error
        self.is_debug = is_debug

class InputInterrput(Exception):pass

class ArgoFrame(Frame):

    class CMDInput(zhTextInput):
        key_maps = zhTextInput.key_maps.copy()
        key_maps.update({
                ac.k_ctrl_c : "finish"
                })
        def finish(self):
            raise InputInterrput
    
    _reader = CMDInput()
    
    def render(self,string,*args):
        '''
        Write string % dict if has any key/value arguments,
        Or just print write to remote.
        '''
        if args :
            self.write( zh_format(string,*args) )
        else:
            self.write(string)

    def desc_dict(self,dic,prompt=''):
        self.writeln(prompt)        
        d = dic.items()
        ds = map(lambda x: zh_format(' %20s | %s',*x),d)
        self.writeln('\r\n'.join(ds))
        self.writeln('\r\n')

    def read_form(self,bases,attrs):
        d = {}
        reader = self.load(self._reader)
        for attr in attrs:
            self.write('%s[%s]:' % (attr,bases.get(attr) or ''))
            r = reader.readln()
            if r :
                d[attr] = r
        return d

    def show_table(self,format_str,thead,content):
        self.writeln( zh_format_d(format_str,**thead))
        self.writeln('-' * len(format_str))
        if content :
            pp = map(lambda x : zh_format_d(format_str,**x),
                     content)
            self.writeln('\r\n'.join(pp))
        else:
            self.writeln('Empty -- \r\n')

    @property
    def user(self):
        '''
        Alias for self.session.user
        '''
        return self.session.user

    def debug(self):
        pass

    @debug_if_debug
    def loop(self):
        reader = self.load(self._reader,
                           prompt='[32margo:[33m%s[0m $ ' % \
                               self.__mark__)
        while True :
            cmd = reader.readln()
            self._eval(cmd)

    def _eval(self,cmd):
        arr = cmd.split(' ')
        action = 'do_' + arr[0]
        args = arr[1:]
        if hasattr(self,action) :
            try:
                getattr(self,action)(*args)
            except ActionInterrupt,e:
                self.writeln(e.info)
                if e.is_error :
                    self.close()
                if e.is_debug :
                    print e.info
            except TypeError:
                traceback.print_exc()
                self.writeln('Something happend.')
            else:
                self.writeln('CMD %s DONE' % action)
        else:
            self.writeln('No Such Command. Type `help` for help.')

    def do_help(self):
        self.writeln(static['help/%s'%self.__mark__])

    do_ = do_help        

    def initialize(self):
        pass

@mark('welcome')
class WelcomeFrame(ArgoFrame):

    def initialize(self):
        super(WelcomeFrame,self).initialize()
        self.do_help()

    def do_auth(self,userid='guest',passwd=None):
        authobj = manager.auth.login(userid,passwd,self.session.ip)
        if authobj :
            self.session.user = authobj
            self.goto('main')
        raise ActionInterrupt(authobj.content)

    def debug(self):
        pass

    def do_register(self):
        d = self.read_form({},["userid","password"])
        manager.auth.register(d['userid'],d['password'])

class AuthedFrame(ArgoFrame):

    @property
    def is_super(self):
        return self.session.userid == 'argo'

    @property
    def user(self):
        return self.session.user

    @property
    def userid(self):
        return self.session.user.userid

    @property
    def seid(self):
        return self.session.user.seid

    def do_mail(self):
        self.goto('mail')

    def do_me(self):
        m = manager.userinfo.get_user(self.userid)
        self.desc_dict(m)        

@mark('main')
class MenuFrame(AuthedFrame):

    able_to_go = ["boardlist","bye"]

    desc = {
        "boardlist":u"讨论区列表",
        "bye":u"离开本站",
        }

    def do_show(self):
        self.writeln(u'''可能的去处：\r\n''')
        for index,data in enumerate(self.able_to_go):
            self.writeln(' %s. %-10s %s' % (index,data,self.desc[data]))
        self.writeln()

    def do_goto(self,num):
        try:
            num = int(num)
        except:
            raise ActionInterrupt('Unvailed places number.')
        if num >= 0 and num < len(self.able_to_go) :
            self.goto(self.able_to_go[num])
        else:
            raise ActionInterrupt('No such places.')

    def debug(self):
        pass

@mark('boardlist')
class BoardListFrame(AuthedFrame):

    def do_sections(self,format_str='%(sid)4s) | %(sectionname)-20s | %(description)-30s'):
        sections = manager.section.get_all_section()
        self.writeln(format_str % dict(sid='Sid',sectionname='Sectionname',
                                       description='Description'))
        sections = map(lambda x :zh_format_d(format_str, **x),sections)
        self.writeln('\r\n'.join(sections))
        self.writeln()

    def do__get(self,sid):
        self.boards = manager.board.get_by_sid(sid)
        self.writeln('Get board by sid [%s] ...' % sid)

    def do_get(self,sid):
        self.do__get(sid)
        self.do_display()
        
    def do__all(self):
        self.boards = manager.board.get_all_board()
        self.writeln('Get all board ...')

    def do_all(self):
        self.do__all()
        self.do_display()

    def do_display(self,start=0,end=-1,
                   format_str='%(bid)4s | %(boardname)20s | %(description)20s | %(bm)s'):
        try:
            start = int(start)
            end = int(end)
        except ValueError:
            raise ActionInterrupt('Start and end need to be number.')
        if end != -1 :
            boards = self.boards[start:end]
        else:
            boards = self.boards[start:]
        self.show_table(format_str,
                        dict(bid='bid',boardname='boardname',
                             description='description',bm='bm'),
                        boards)
        self.writeln('\r\n')

    def do_recommend(self):
        self.boards = manager.board.get_recommend()
        self.do_display()

    def do_addr(self,bid):
        self.writeln('Add [%s] to recommend. ' % bid)
        manager.board.add_recommend(bid)

    def do_delr(self,bid):
        self.writeln('Del [%s] from recommend. ' % bid)
        manager.board.del_recommend(bid)

    def do_desc(self,bid):
        board = manager.board.get_board_by_id(bid)
        if board is not None:
            self.desc_dict('DESC Board :\r\n',board)
        else:
            raise ActionInterrupt('No such board.')

    def do_addb(self):
        try:
            d = self.read_form({},['sid','boardname','description',
                                   'bm','flag','tp','r_perm','p_perm'])
            self.desc_dict(d,prompt='Realy?')
            manager.board.add_board(**d)
        except InputInterrput:
            self.writeln('User skip the input.')

    def do_updateb(self,bid):
        try:
            b = manager.get_board_by_id(bid)
            d = self.read_form(b,["sid","boardname","description","bm","flag",
                                  "total","topic_total","tp","r_per","p_perm"])
            manager.board.update_board(bid,**d)
        except InputInterrput:
            self.writeln("User skip the input.")

    def do_deleteb(self,bid):
        manager.board.del_board(bid)

    def do_adds(self,sectionname,description):
        manager.section.add_section(sectionname=sectionname,description=description)

    def do_deletes(self,sid):
        manager.section.del_section(sid)

    def do_enter(self,bid):
        self.goto('post',bid)

    def do_r(self):
        self.goto('main')

    def debug(self):
        # self._eval('enter 1')
        pass

@mark('post')
class PostFrame(AuthedFrame):

    def initialize(self,bid):
        self.do_enter(bid)
        self.offset = 0
        
    def do_enter(self,bid):
        self.bid = bid
        self.boardname = manager.board.id2name(bid)
        self.cond = (20,'pid',None,None)

    def do_list(self,offset=None,limit=20,order='pid',mark=None,reverse=None):
        self.cond = (limit,order,mark,reverse)
        if offset is not None:
            self.offset = offset
        self.do_l()
        
    def do_l(self,format_str='%(pid)4s | %(title)15s | %(owner)s'):
        posts = manager.post.get_posts_advan(self.boardname,self.offset,*self.cond)
        self.writeln('Offset [%s] %s\r\n' % (self.offset,self.cond))
        self.show_table(format_str,
                        dict(pid='pid',title='title',owner='owner'),
                        posts)
        if posts :
            self.offset += 20
        else:
            self.offset = 0

    def do_board(self):
        d = manager.board.get_board_by_id(self.bid)
        self.writeln('Current Board [%s] ' % self.boardname)
        self.desc_dict(d)

    def format_post(self,post):
        d = '[%s]\r\n%s\r\n%s\r\n by %s\r\n\r\n%s' % (
            post['pid'],
            post['title'],'=' * 20,
            post['owner'],post['content'])
        return d

    def _read(self,post):
        pf = self.format_post(post)
        self.writeln(pf)

    def do_(self,pid=None):
        if pid is not None:
            self.offset = pid
        if self.offset is None:
            self.offset = 0
        p = manager.post.get_post(self.boardname,self.offset)
        if p:
            self._read(p)
        self.offset = manager.post.next_post_pid(self.boardname,self.offset)

    def read_post(self):
        p = {}
        reader = self.load(self._reader)
        p['title'] = reader.readln(prompt='Title: ')
        p['content'] = reader.readln()
        return p
    
    def do_new(self):
        p = self.read_post()
        manager.action.new_post(self.boardname,self.userid,**p)

    def do_reply(self,pid=None):
        p = self.read_post()
        if pid == None:
            self.writeln('Reply to [%s]' % self.offset)
            pid = self.offset
        manager.action.reply_post(self.boardname,self.userid,**p)

    def do_edit(self,pid=None):
        p = self.read_post()
        if pid == None :
            self.writeln('Edit [%s]' % self.offset)
            pid = self.offset
        manager.action.update_post(self.boardname,self.userid,pid,
                                   **p)

    def do_r(self):
        self.goto('boardlist')

@mark('mail')
class MailFrame(AuthedFrame):

    def initialize(self):
        super(MailFrame,self).initialize()
        self.offsets = 0
        self.offsetr = 0

    def do_f(self,format_str='%(mid)5s | %(fromuserid)-10s | %(content)s'):
        mails = manager.action.get_rebox_mail(self.userid,offset=self.offsetr)
        self.writeln('Offsetr [%s] \r\n' % self.offsetr)
        self.show_table(format_str,
                        dict(mid='ID',fromuserid='FROM',touserid='TO',content='content'),
                        mails)
        if mails :
            self.offsetr += 20
        else:
            self.offsetr = 0

    def do_s(self):
        d = self.read_form({},["touserid","content"])
        manager.action.send_mail(self.userid,**d)

    def do_del(self,mid):
        manager.action.del_mail(self.userid,mid)

    mail_template = static['mail']
    def format_mail(self,mail):
        return self.mail_template.safe_substitute(mail)

    def do_read(self,mid):
        d = manager.action.get_mail(self.userid,mid)
        self.writeln(self.format_mail(d))

# @mark('disgest')
# class DisgestFrame(AuthedFrame):

#     def do_f(self,format_str='%(id)s %(title)s %(owner)s %(mtime)s')
#         posts = manager.disgest.get_all_books(self.partname)
#         self.show_table(format_str,
#                         dict(id='id',title='title',owner='owner',mtime='mtime'),
#                         posts)

if __name__ == '__main__' :
    s = Server(mark['welcome'])
    s.run()
