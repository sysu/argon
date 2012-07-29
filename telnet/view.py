#!/usr/bin/python2
# -*- coding: utf-8 -*-

from chaofeng.g import mark
from chaofeng.ui import Animation,LongTextBox,TextEditor
from chaofeng import ascii as ac
from libframe import BaseAuthedFrame,BaseTextBoxFrame
from model import manager
from datetime import datetime
import config
import re

@mark('view_text')
class ViewTextFrame(BaseTextBoxFrame):

    def get_text(self):
        return self.text

    def initialize(self, text):
        self.text = text
        super(ViewTextFrame, self).initialize()
        
@mark('post')
class ReadPostFrame(BaseTextBoxFrame):

    @classmethod
    def try_jump(self,args):
        try:
            if manager.query.get_post(self.userid, args[0], args[1]) :
                return dict(boardname=args[0],
                            pid=args[1])
        except:
            return False

    def get_post(self, board, pid):
        return manager.query.get_post(self.userid, board, pid)

    def wrapper_post(self,post):
        return self.render_str('post-t',post=post)

    def get_text(self):
        return self.text
        
    def initialize(self, board, pid):

        if not board['perm'][0] :
            self.writeln(u"错误的讨论区或你没有权限！")
            self.pause()
            self.goto_back()

        self.board = board
        self._read_post(board['boardname'], pid)
        super(ReadPostFrame,self).initialize()

    def getdesc(self):
        return u'阅读文章            -- [%s](/p/%s/%s)' % (self.post['title'], self.boardname, self.pid)

    def _read_post(self, boardname, pid):
        self.boardname, self.pid = boardname, pid
        self.post = self.get_post(self.board, pid)
        self.session['lastboard'] = boardname
        self.session['lastpid'] = pid
        self.session['lasttid'] = self.post.tid
        self.text = self.wrapper_post(self.post)
        manager.readmark.set_read(self.userid, self.boardname, self.pid)

    def reset_post(self, boardname, pid):
        if pid :
            self._read_post(boardname, pid)
            self.reset_text(self.text)

    def next_post(self):
        return self.boardname, manager.post.next_post_pid(self.boardname,self.pid)

    def prev_post(self):
        return self.boardname, manager.post.prev_post_pid(self.boardname,self.pid)

    def finish(self,args=None):
        if args is True:
            self.reset_post(*self.next_post())
        if args is False:
            self.reset_post(*self.prev_post())
        if args is None:
            self.goto_back()

@mark('view_clipboard')
class ViewClipboardFrame(BaseTextBoxFrame):

    def get_text(self):
        return manager.clipboard.get_clipboard(self.userid)

    def finish(self, a=None):
        self.goto_back()

# def goto_link(mark):    

# @mark('help')
# class TutorialFrame(TextBoxFrame):

#     @classmethod
#     def try_jump(cls,args):
#         print args[0]
#         if args[0] in config.have_help_page :
#             return dict(page=args[0])

#     def getdesc(self):
#         return u'查看帮助            -- [](/h/%s)' % self.page
    
#     def initialize(self,page='index'):
#         super(TutorialFrame,self).initialize()
#         self.setup()
#         self.page = page
#         self.set_text(self.render_str('help/%s'%page))

#     def finish(self,args=None):
#         self.goto_back()

#     def show_help(self):
#         self.suspend('help',page='help')
