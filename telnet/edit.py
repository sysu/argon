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
import random
from libdecorator import need_perm

@mark('new_post')
class NewPostFrame(BaseEditFrame):

    prompt = u'[1;32m0[m~[1;32m%s[m/[1;32mx[m 选择/随机签名档 [1;32mt[m标题，[1;32mu[m回复，[1;32mq[m放弃:'
    
    def update_attr(self, attrs):
        self.write(''.join([ac.move2(21,1),
                            ac.clear1,
                            self.render_str('edit_head', **attrs)]))

    def read_attrs(self):
        sign_num = manager.usersign.get_sign_num(self.userid)
        attrs = {
            "boardname":self.boardname,
            "replyable":True,
            "usesign":0,
            "title":u"[正在设定主題]",
            }
        if sign_num :
            attrs['usesign'] = random.randint(1, sign_num)
        self.update_attr(attrs)
        attrs['title'] = self.readline_safe(prompt=u'请输入标题：', buf_size=40)
        if not attrs['title'] :
            return
        self.update_attr(attrs)
        prompt = ''.join([ac.move2(25,1), ac.kill_line, self.prompt % sign_num])
        while True:
            op = self.readline_safe(buf_size=4, prompt=prompt)
            if op == '':
                break
            elif op is False or op=='q':
                return None
            elif op == 't' :
                attrs['title'] = self.readline_safe(prompt=u'\r\x1b[K请输入标题：',
                                                    prefix=attrs['title'],buf_size=40)
                if not attrs['title'] :
                    return
            elif op == 'u' :
                attrs['replyable'] = not attrs['replyable']
            elif op == 'x' and sign_num:
                attrs['usesign'] = random.randint(1, sign_num)
            elif op.isdigit() :
                n = int(op)
                if n <= sign_num :
                    attrs['usesign'] = n
            self.update_attr(attrs)
        return attrs

    def check_perm(self, board):
        _,w,_,_ = manager.query.get_board_ability(self.session.user.userid, board['boardname'])
        return w or u'该版禁止发文或你没有相应的权限！'

    @need_perm
    def initialize(self, board):
        self.boardname = board['boardname']
        self.cls()
        self.attrs = self.read_attrs()
        if self.attrs :
            sign = manager.usersign.get_sign(self.userid, self.attrs['usesign']-1) \
                if self.attrs['usesign'] else ''            
            text = self.render_str('base_post-t', sign=sign)
            super(NewPostFrame, self).initialize(text=text)
            self.message(u'写新文章 -- %s' % self.attrs['title'])
        else:
            self.write(u'放弃发表新文章')
            self.pause()
            self.goto_back()

    def finish(self):
        manager.action.new_post(self.boardname,
                                self.userid,
                                self.attrs['title'],
                                self.fetch_all(),
                                self.session.ip,
                                config.BBS_HOST_FULLNAME,
                                replyable=self.attrs['replyable'])
        self.message(u'发表文章成功！')
        self.pause()
        self.goto_back()

@mark('reply_post')
class ReplyPostFrame(BaseEditFrame):

    def check_perm(self, boardname, pid):
        _,w,_,_ = manager.query.get_board_ability(self.session.user.userid, board['boardname'])
        w = w and post.replyable
        return w or u'该版禁止发文或你没有相应的权限！'

    prompt = u'[1;32m0[m~[1;32m%s[m/[1;32mx[m 选择/随机签名档 [1;32mt[m标题，[1;32mu[m回复，[1;32mq[m放弃:'
    
    def update_attr(self, attrs):
        self.write(''.join([ac.move2(21,1),
                            ac.clear1,
                            self.render_str('edit_head', **attrs)]))

    def read_attrs(self):
        sign_num = manager.usersign.get_sign_num(self.userid)
        attrs = {
            "boardname":self.boardname,
            "replyable":True,
            "usesign":0,
            "title":self.title,
            }
        if sign_num :
            attrs['usesign'] = random.randint(1, sign_num)
        self.update_attr(attrs)
        prompt = ''.join([ac.move2(25,1), ac.kill_line, self.prompt % sign_num])
        while True:
            op = self.readline_safe(buf_size=4, prompt=prompt)
            if op == '':
                break
            elif op is False or op=='q':
                return None
            elif op == 't' :
                attrs['title'] = self.readline_safe(prompt=u'\r\x1b[K请输入标题：',
                                                    prefix=attrs['title'],buf_size=40)
                if not attrs['title'] :
                    return
            elif op == 'u' :
                attrs['replyable'] = not attrs['replyable']
            elif op == 'x' and sign_num:
                attrs['usesign'] = random.randint(1, sign_num)
            elif op.isdigit() :
                n = int(op)
                if n <= sign_num :
                    attrs['usesign'] = n
            self.update_attr(attrs)
        return attrs

    # @need_perm
    def initialize(self, boardname, post):
        self.cls()
        self.boardname = boardname
        self.replyid = post['pid']
        self.title = post['title'] if post['title'].startswith('Re:')\
            else 'Re: %s' % post['title']
        self.attrs = self.read_attrs()
        super(ReplyPostFrame, self).initialize()
        self.message(u'回复文章 -- %s' % self.title)

    def finish(self):
        manager.action.reply_post(
            self.boardname,
            self.userid,
            self.title,
            self.fetch_all(),
            self.session.ip,
            config.BBS_HOST_FULLNAME,
            self.replyid,
            replyable=True)
        self.message(u'回复文章成功！')
        self.pause()
        self.goto_back()

@mark('edit_post')
class EditPostFrame(BaseEditFrame):

    def check_perm(self, board, post):
        # _,w,_,_ = manager.query.get_board_ability(self.session.user.userid, board['boardname'])
        # return (w or u'该版禁止发文或你没有相应的权限！') and
        return (post.owner == self.userid) or u'你没有编辑此文章的权限！'

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
