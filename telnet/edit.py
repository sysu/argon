#!/usr/bin/python2
# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import mark
from model import manager
from libframe import BaseAuthedFrame,BaseEditFrame
from datetime import datetime
import config
from libdecorator import need_perm

@mark('new_post')
class NewPostFrame(BaseEditFrame):

    def check_perm(self, board):
        _,w,_,_ = manager.query.get_board_ability(self.session.user.userid, board['boardname'])
        return w or u'该版禁止发文或你没有相应的权限！'

    @need_perm
    def initialize(self, board):
        self.boardname = board['boardname']
        self.cls()
        self.title = self.read_title(prompt=u'请输入标题：')
        if self.title :
            super(NewPostFrame, self).initialize()
            self.message(u'写新文章 -- %s' % self.title)
        else:
            self.message(u'放弃发表新文章')
            self.pause()
            self.goto_back()

    def finish(self):
        manager.action.new_post(self.boardname,
                                self.userid,
                                self.title,
                                self.fetch_all(),
                                self.session.ip,
                                config.BBS_HOST_FULLNAME)
        self.message(u'发表文章成功！')
        self.pause()
        self.goto_back()

@mark('reply_post')
class ReplyPostFrame(BaseEditFrame):

    def check_perm(self, board, post):
        _,w,_,_ = manager.query.get_board_ability(self.session.user.userid, board['boardname'])
        return w or u'该版禁止发文或你没有相应的权限！'

    @need_perm
    def initialize(self, board, post):
        self.cls()
        self.boardname = board['boardname']
        self.replyid = post['pid']
        if post['title'].startswith('Re:'):
            title = post['title']
        else:
            title = 'Re: %s' % post['title']
        self.title = self.read_title(prompt=u'请输入标题：',prefix=title)
        super(ReplyPostFrame,self).initialize()

    def finish(self):
        manager.action.reply_post(
            self.boardname,
            self.userid,
            self.title,
            self.fetch_all(),
            self.session.ip,
            config.BBS_HOST_FULLNAME,
            self.replyid)
        self.message(u'回复文章成功！')
        self.pause()
        self.goto_back()

@mark('edit_post')
class EditPostFrame(BaseEditFrame):

    def check_perm(self, board, post):
        _,w,_,_ = manager.query.get_board_ability(self.session.user.userid, board['boardname'])
        return w or u'该版禁止发文或你没有相应的权限！'

    @need_perm
    def initialize(self, board, post):
        self.cls()
        self.boardname = board['boardname']
        self.pid = post['pid']
        super(EditPostFrame, self).initialize(text=post['content'])
        self.message(u'开始编辑文章')
        
    def finish(self):
        manager.action.update_post(self.boardname,
                                   self.userid,
                                   self.pid,
                                   self.fetch_all())
        self.message(u'编辑文章成功！')
        self.pause()
        self.goto_back()

@mark('edit_text')
class EditFileFrame(BaseEditFrame):

    def initialize(self, filename, callback, text='', l=0, split=False):
        self.cls()
        self.filename = filename
        self.split = split
        self.callback = callback
        super(EditFileFrame, self).initialize(text=text, spoint=l)
        self.message(u'开始编辑档案 -- %s' % filename)

    def finish(self):
        self.message(u'修改档案结束!')
        if self.split:
            self.callback(filename=self.filename, text=self.fetch_lines())
        else:
            self.callback(filename=self.filename, text=self.fetch_all())
        self.pause()
        self.goto_back()

    def quit_iter(self):
        self.message(u'放弃本次编辑操作？')
        d = self.readline()
        if not d :
            self.goto_back()

@mark('edit_clipboard')
class EditorClipboardFrame(BaseEditFrame):

    def initialize(self):
        super(EditorClipboardFrame, self).initialize(text=self.get_text())

    def finish(self):
        manager.clipboard.set_clipboard(self.userid, self.fetch_all())
        self.message(u'更新暂存档成功！')
        self.pause()
        self.goto_back()

    def get_text(self):
        return self.u(manager.clipboard.get_clipboard(self.userid))
