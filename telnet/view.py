#!/usr/bin/python2
# -*- coding: utf-8 -*-

from chaofeng.g import mark
from chaofeng.ui import Animation,LongTextBox,TextEditor,NullValueError
from chaofeng import ascii as ac
from libframe import BaseAuthedFrame,BaseTextBoxFrame
from model import manager
from datetime import datetime
from libdecorator import need_perm
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

    # @classmethod
    def try_jump(self,args):
        try:
            r = manager.query.get_board_ability(self.userid, args[0])[0]
            if r and manager.post.get_post(args[0], args[1]) :
                return dict(boardname=args[0],
                            pid=args[1])
        except :
            return False

    def get_post(self, board, pid):
        return manager.post.get_post(board['boardname'], pid)

    def wrapper_post(self,post):
        return self.render_str('post-t',post=post)

    def get_text(self):
        return self.text

    def check_perm(self, boardname, pid):
        r = manager.query.get_board_ability(self.session.user.userid, boardname)[0]
        return r or u"错误的讨论区或你没有权限！"

    @need_perm
    def initialize(self, boardname, pid):
        if hasattr(self, 'lastboard') and self.lastboard.boardname != boardname :
            manager.action.enter_board(self.userid, self.seid, boardname)
            try:
                index = map(lambda x:x['boardname'], self.boards).index(boardname)
            except ValueError:  ############  impossible
                self.pause()
                self.goto_back()
            self.session.lastboard = self.get_board_by_name(boardname)
        self.board = board = self.session.lastboard
        try:
            self._read_post(board['boardname'], pid)
        except NullValueError as e:
            self.write(e.message)
            self.pause()
            self.goto_back()
        super(ReadPostFrame,self).initialize()

    def getdesc(self):
        return u'阅读文章            -- [%s](/p/%s/%s)' % (self.post['title'], self.boardname, self.pid)

    def _read_post(self, boardname, pid):
        post = self.get_post(self.board, pid)
        if post :
            self.boardname, self.pid = boardname, pid
            self.post = self.get_post(self.board, pid)
            self.session['lastboard'] = boardname
            self.session['lastpid'] = pid
            self.session['lasttid'] = self.post.tid
            self.text = self.wrapper_post(self.post)
            manager.readmark.set_read(self.userid, self.boardname, self.pid)
        else:
            raise NullValueError(u'没有此文章')

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

    def reply_post(self):
        _,w,_,_ = manager.query.get_board_ability(self.userid, self.session.lastboard['boardname'])
        w = w and self.post.replyable
        if w :
            self.suspend('reply_post', boardname=self.boardname, post=self.post)
        else:
            self.message(u'该文章禁止回复！')

@mark('view_clipboard')
class ViewClipboardFrame(BaseTextBoxFrame):

    def get_text(self):
        return manager.clipboard.get_clipboard(self.userid)

    def finish(self, a=None):
        self.goto_back()

@mark('help')
class TutorialFrame(BaseTextBoxFrame):

    # @classmethod
    def try_jump(cls,args):
        if 'help/%s' % args[0] in config.all_help_file :
            return dict(page=args[0])

    def getdesc(self):
        return u'查看帮助            -- [](/h/%s)' % self.page

    def initialize(self,page='index'):
        self.page = page
        super(TutorialFrame,self).initialize()

    def get_text(self):
        print self.page
        return self.render_str('help/%s' % self.page)

    def finish(self,args=None):
        self.goto_back()
