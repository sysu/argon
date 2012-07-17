# -*- coding: utf-8 -*-
from chaofeng.g import mark
from chaofeng.ui import Animation,LongTextBox,TextEditor
from chaofeng import ascii as ac
from argo_frame import ArgoFrame,zh_format
from model import manager
from datetime import datetime
import config
import re

class ArgoTextBox(LongTextBox):

    def bottom_bar(self,msg):
        self.write(ac.move2(24,1))
        self.frame.render('bottom_view', message=msg, s=self.s, maxs=self.max)

class ArgoTextBoxFrame(ArgoFrame):

    '''
    Inherit this class and call the `set_text` method
    to display the text.
    It's useful to copy the `key_maps` and `textbox_cmd`
    and add new key/value into them.
    '''

    def setup(self):
        self.textbox = self.load(ArgoTextBox)
        self.textbox.bind(self.finish)

    def restore(self):
        self.textbox.refresh_all()
        self.bottom_bar()

    def set_text(self,text):
        self.textbox.set_text(text)
        self.textbox.refresh_all()
        self.bottom_bar()
        
    def get(self,data):
        if data in config.hotkeys['view_textbox']:
            getattr(self.textbox, config.hotkeys['view_textbox'][data])()
            self.bottom_bar()
        self.try_action(config.hotkeys['view'].get(data))

    def bottom_bar(self,msg=''):
        self.textbox.bottom_bar(msg)

    def _go_link(self,line):
        s = line.split()
        if (len(s) > 0) and (s[0] in self.jump_marks) :
            m = s[0]
            status = mark[m].try_jump(s)
            if status :
                self.suspend(m,**status)            

    def go_link(self):
        self.write(ac.move2(24,1) + ac.kill_line)
        d = self.readline()
        self._go_link(d)
        self.bottom_bar()

    links_re = re.compile(r'\[[^\]]*\]\(/(p)/(.+)/(\d+)\)|'
                          r'\[[^\]]*\]\(/(h)/(.+)\)')

    jump_marks = {
        'p':'post',
        'h':'help',
        }

    def hint_link(self,t):
        if t[0] == 'p' :
            self.links_args = t[0],t[1:3]
            return u'去看 %s 区的 %s 号文？' % (t[1],t[2])
        elif t[3] == 'h' :
            self.links_args = t[3],t[4:5]
            return u'去看 %s 的帮助页面？' % (t[4])
        return u'错误的跳转标记'

    def check_jump(self):
        n = self.jump_marks[self.links_args[0]]
        r = mark[n].try_jump(self.links_args[1])
        if r :
            self.suspend(n,**r)
        else:
            self.bottom_bar(u'不是一个有效的跳转标志')
            return

    def find_options(self, opstring):
        for row in range(0, self.limit):
            col = self.lines.find( opstring )
            if col != - 1:
                return row,col
        return None

    def re2str(self, reop):
        return

    def select_and_jump(self,text):
        options = re.findall(self.links_re,text)
        if not options :
            self.bottom_bar(u'没有可用的跳转标志')
            return
        self.select_start = 0
        res = self.select(lambda x :
                              self.bottom_bar(self.hint_link(x)),
                          options)
        if res is False :
            self.bottom_bar(u'放弃跳转')
        else:
            self.check_jump()

    def jump_from_screen(self):
        text,self.lines = self.textbox.getscreen_with_raw()
        self.select_and_jump(text)

    def show_help(self):
        self.suspend('help',page='view')

    def message(self,msg):
        self.bottom_bar(msg)

    # def jump_man(self):
    #     self.bottom_bar(u'前往：')
    #     self.write(ac.bg_blue)
    #     text = self.readline()
    #     self.select_and_jump('[](%s)' % text)
        
@mark('post')
class ArgoReadPostFrame(ArgoTextBoxFrame):

    @classmethod
    def try_jump(self,args):
        try:
            if manager.post.get_post(args[0],args[1]) :
                return dict(boardname=args[0],
                            pid=args[1])
        except:
            return False            

    def initialize(self,boardname,pid):
        super(ArgoReadPostFrame,self).initialize()
        self.setup()
        self.set_post(boardname,pid)

    @property
    def status(self):
        return dict(boardname=self.boardname,
                    pid=self.pid)

    @classmethod
    def describe(self,s):
        return u'阅读文章            -- [%s](/p/%s/%s)' % (manager.post.pid2title(**s),
                                                           s['boardname'],s['pid'])
                                     
    def get_post(self,boardname,pid):
        return manager.post.get_post(boardname,pid)

    def wrapper_post(self,post):
        return self.render_str('post-t',post=post)

    def set_post(self,boardname,pid):
        if pid is not None:
            self.boardname,self.pid = boardname,pid
            self.post = self.get_post(boardname,pid)
            self.session['lastboard'] = boardname
            self.session['lastpid'] = pid
            self.session['lasttid'] = self.post.tid
            self.text = self.wrapper_post(self.post)
            self.cls()
            manager.readmark.set_read(self.userid, self.boardname, self.pid)
            self.set_text(self.text)

    def next_post(self):
        return self.boardname,manager.post.next_post_pid(self.boardname,self.pid)

    def prev_post(self):
        return self.boardname,manager.post.prev_post_pid(self.boardname,self.pid)

    def finish(self,args=None):
        if args is True:
            self.set_post(*self.next_post())
        if args is False:
            self.set_post(*self.prev_post())
        if args is None:
            self.goto_back()

@mark('help')
class TutorialFrame(ArgoTextBoxFrame):

    @classmethod
    def try_jump(cls,args):
        if args[0] in config.have_help_page :
            return dict(page=args[0])

    @property
    def status(self):
        return dict(page=self.page)

    @classmethod
    def describe(self,s):
        return u'查看帮助            -- [](/h/%s)' % s['page']
    
    def initialize(self,page='index'):
        super(TutorialFrame,self).initialize()
        self.setup()
        self.page = page
        self.set_text(self.render_str('help/%s'%page))

    def finish(self,args=None):
        self.goto_back()

    def show_help(self):
        self.suspend('help',page='help')
