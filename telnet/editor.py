# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import mark
from chaofeng.ui import TextEditor
from model import manager
from argo_frame import ArgoFrame
from libtelnet import zh_format
from datetime import datetime
import config

class ArgoEditor(TextEditor):

    def bottom_bar(self,msg=''):
        self.write(ac.move2(24,0))
        self.frame.render('bottom_edit', message=msg, l=self.l, r=self.r)
        self.fix_cursor()

class EditFrame(ArgoFrame):

    def setup(self):
        self.e = self.load(ArgoEditor, height=23, hislen=5, dis=10)
        self.ugly = ''  # 修复单字节发送的bug （sterm）

    def reset(self, text=u'', l=0):
        self.e.set_text(self.u(text),l)
        self.e.refresh_all()

    def restore(self):
        self.e.do_command("refresh")
        
    def get(self,char):

        if self.ugly :
            char = self.ugly + char
            self.ugly = ''
        elif len(char) == 1 and self.is_gbk_zh(char):
            self.ugly = char
            return
            
        if char in config.hotkeys['edit_editor'] :
            self.e.do_command( config.hotkeys['edit_editor'][char])
        elif char == config.hotkeys['edit_2ndcmd_start'] :
            x = self.read_secret()
            if x in config.hotkeys['edit_editor_2nd']:
                self.e.do_command(config.hotkeys['edit_editor_2nd'][x])
        elif char in config.hotkeys['edit']:
            getattr(self,config.hotkeys['edit'][char])()
        else:
            self.e.safe_insert_iter(char)

    def finish(self):
        print self.e.getall()

    def message(self,content):
        self.e.bottom_bar(content[:40])

    def quit_iter(self):
        self.message(u'放弃本次编辑操作？')
        d = self.readline()
        if not d :
            self.goto_back()

    def show_help(self):
        self.suspend('help',page='edit')

@mark('new_post')
class NewPostFrame(EditFrame):

    def initialize(self,boardname):
        super(NewPostFrame,self).initialize()
        self.boardname = boardname
        self.read_title()
        self.setup()
        self.reset()
        self.message(u'文章标题设置为 %s' % self.title)
        
    @property
    def status(self):
        return dict(boardname=self.boardname)

    @classmethod
    def describe(self,s):
        return '发表文章 -- %s' % s.boardname

    def _read_title(self):
        self.write(ac.move2(24,1) + ac.kill_line + u'文章标题：')
        return self.readline()

    def read_title(self):
        d = self._read_title()
        if not d :
            self.pause(u'放弃发表文章')
            self.goto_back()
        else:
            self.title = d

    def finish(self):
        manager.action.new_post(self.boardname,
                                self.userid,
                                self.title,
                                self.e.getall(),
                                self.session.ip,
                                config.BBS_HOST_FULLNAME)
        self.message(u'发表文章成功！')
        self.pause()
        self.goto_back()

@mark('reply_post')
class ReplyPostFrame(NewPostFrame):

    def initialize(self,boardname,replyid):
        super(ReplyPostFrame,self).initialize(boardname)
        self.replyid = replyid
        self.setup()
        self.reset()

    @property
    def status(self):
        return dict(boardname=self.boardname,
                    replyid=self.replyid)

    @classmethod
    def describe(self,s):
        return '回复文章 -- %s -- %s' % (s.boardname,s.replyid)

    def finish(self):
        manager.action.reply_post(
            self.boardname,
            self.userid,
            self.title,
            self.e.getall(),
            self.session.ip,
            config.BBS_HOST_FULLNAME,
            self.replyid)
        self.message(u'回复文章成功！')
        self.pause()
        self.goto_back()

@mark('edit_post')
class EditPostFrame(EditFrame):

    def initialize(self,boardname,pid):
        super(EditPostFrame,self).initialize()
        self.boardname = boardname
        self.pid = pid
        self.setup()
        self.reset()
        self.message(u'开始编辑文章')
        
    @property
    def status(self):
        return dict(boardname=self.boardname,
                    pid=pid)

    @classmethod
    def describe(self,s):
        return '编辑文章 -- %s -- %s' % (s.boardname,
                                         s.pid)   

    def finish(self):
        manager.action.update_post(self.boardname,
                                   self.userid,
                                   self.pid,
                                   self.e.getall())
        self.message(u'编辑文章成功！')
        self.goto_back()

@mark('edit_text')
class EditFileFrame(EditFrame):

    def initialize(self, filename, text='', l=0, split=False):
        super(EditFrame, self).initialize()
        self.split = split
        self.setup()
        print repr(text)
        self.reset(text, l)
        self.message(u'开始编辑档案 -- %s' % filename)

    @classmethod
    def describe(self,s):
        return '编辑档案 -- %s' % s.filename

    def finish(self):
        if self.split:
            self.pipe = self.e.get_all_lines()
        else:
            self.pipe = self.e.getall()
        self.message(u'修改档案结束!')
        self.goto_back()

    def quit_iter(self):
        self.message(u'放弃本次编辑操作？')
        d = self.readline()
        if not d :
            print 'Cancel'
            self.pipe = None
            self.goto_back()
