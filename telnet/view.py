# -*- coding: utf-8 -*-
from chaofeng import static
from chaofeng.g import mark
from chaofeng.ui import Animation,LongTextBox,TextEditor
from chaofeng import ascii as ac
from argo_frame import ArgoFrame,zh_format
from model import manager
from common import post_render#,help_render
from datetime import datetime
import re

class ArgoTextBox(LongTextBox):

    bottom_txt = ac.move2(24,1) + static['bottom_bar/text_view'] + ac.reset
    
    def bottom_bar(self,msg):
        self.write(zh_format(self.bottom_txt,self.s,self.max,
                             datetime.now().ctime(),msg))

class ArgoTextBoxFrame(ArgoFrame):

    '''
    Inherit this class and call the `set_text` method
    to display the text.
    It's useful to copy the `key_maps` and `textbox_cmd`
    and add new key/value into them.
    '''

    _textbox = ArgoTextBox()
    key_maps = ArgoFrame.key_maps.copy()
    key_maps.update({
            "Q":"goto_back",
            ac.k_left:"goto_back",
            ac.k_ctrl_c:"goto_back",
            ac.k_ctrl_u:"go_link",
            "a":"jump_from_screen",
            ac.k_ctrl_a:"jump_man",
            ac.k_ctrl_r:"jump_history",
            })
    
    textbox_cmd = {
        ac.k_up : "move_up",
        "k":"move_up",
        ac.k_down : "move_down",
        ac.k_right:"move_down",
        "j":"move_down",
        ac.k_ctrl_b:"page_up",
        ac.k_page_up:"page_up",
        ac.k_ctrl_f:"page_down",
        ac.k_page_down:"page_down",
        ac.k_right:"page_down",
        ac.k_home:"go_first",
        ac.k_end:"go_last",
        "$":"go_last",
        }

    def initialize(self):
        super(ArgoTextBoxFrame,self).initialize()
        self.textbox_ = self.load(self._textbox)
        self.textbox_.bind(self.finish)

    def set_text(self,text):
        self.textbox_.set_text(text)
        self.textbox_.refresh_all()
        self.bottom_bar()
        
    def get(self,data):
        if data in self.textbox_cmd:
            getattr(self.textbox_,self.textbox_cmd[data])()
            self.bottom_bar()
        self.try_action(data)

    def bottom_bar(self,msg=''):
        self.textbox_.bottom_bar(msg)

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

    def try_jump(self):
        n = self.jump_marks[self.links_args[0]]
        r = mark[n].try_jump(self.links_args[1])
        if r :
            self.suspend(n,**r)
        else:
            self.bottom_bar(u'不是一个有效的跳转标志')
            return

    def select_and_jump(self,text):
        options = re.findall(self.links_re,text)
        if not options :
            self.bottom_bar(u'没有可用的跳转标志')
            return
        res = self.select(lambda x :
                              self.bottom_bar(self.hint_link(x)),
                          options)
        if res is False :
            self.bottom_bar(u'放弃跳转')
        else:
            self.try_jump()

    def jump_from_screen(self):
        text = self.textbox_.getscreen()
        self.select_and_jump(text)

    def jump_man(self):
        self.bottom_bar(u'前往：')
        self.write(ac.bg_blue)
        text = self.readline()
        self.select_and_jump('[](%s)' % text)

    def jump_history(self):
        self.select(lambda x:
                        self.bottom_bar(self.getdesc(x)),
                    self.history)
        
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
        return post_render.render(post=post)

    def set_post(self,boardname,pid):
        if pid is not None:
            self.boardname,self.pid = boardname,pid
            self.post = self.get_post(boardname,pid)
            self.text = self.wrapper_post(self.post)
            self.cls()
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
        if static.get('help/%s' % args[0]) :
            return dict(page=args[0])

    @property
    def status(self):
        return dict(page=self.page)

    @classmethod
    def describe(self,s):
        return u'查看帮助            -- [](/h/%s)' % s['page']
    
    def initialize(self,page):
        super(TutorialFrame,self).initialize()
        self.page = page
        self.set_text(static['help/%s' % page])

    def finish(self,args=None):
        self.goto_back()
