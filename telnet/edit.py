# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import mark
from chaofeng.ui import TextEditor
from model import manager
from argo_frame import AuthedFrame
from libtelnet import zh_format
from datetime import datetime
import config

class Editor(TextEditor):

    def bottom_bar(self,msg=''):
        self.write(ac.move2(24,0))
        self.frame.render('bottom_edit', message=msg, l=self.l, r=self.r)
        self.fix_cursor()

class EditFrame(AuthedFrame):

    def finish(self):
        raise NotImplementedError

    def restore_screen(self):
        self.e.do_editor_command("refresh")

    def notify(self, msg):
        pass ############           Not ImplamentedError

    def restore(self):
        self.e.do_editor_command("refresh")

    def message(self,content):
        self.e.bottom_bar(content[:40])
        
    def get(self,char):
        if self.ugly :
            char = self.ugly + char
            self.ugly = ''
        elif len(char) == 1 and ac.is_gbk_zh(char):
            self.ugly = char
            return
            
        if char in config.hotkeys['edit_editor'] :
            self.e.do_editor_command( config.hotkeys['edit_editor'][char])
        elif char == config.hotkeys['edit_2ndcmd_start'] :
            x = self.read_secret()
            if x in config.hotkeys['edit_editor_2nd']:
                self.e.do_editor_command(config.hotkeys['edit_editor_2nd'][x])
        elif char in config.hotkeys['edit']:
            getattr(self, config.hotkeys['edit'][char])()
        else:
            self.e.safe_insert_iter(char)

    def copy_to_superclip(self):
        text = self.e.get_clipboard()
        print text
        manager.clipboard.append_clipboard(self.userid, value=text)

    def insert_superclip(self):
        clipboard = self.u(manager.clipboard.get_clipboard(self.userid))
        print clipboard
        self.e.insert_paragraph(clipboard)
        self.restore()
        
    def quit_iter(self):
        self.message(u'放弃本次编辑操作？')
        d = self.readline()
        if not d :
            self.goto_back()

    def show_help(self):
        self.suspend('help',page='edit')

    def initialize(self, spoint=0, text=''):
        self.e = self.load(Editor, height=23, hislen=5, dis=10)
        self.e.set_text(self.u(text), spoint)
        self.ugly = '' # 修复单字节发送的bug （sterm）
        self.restore_screen()

    def read_title(self, prompt='', prefix=''):
        return self.readline(prompt=prompt, prefix=prefix, buf_size=40)

@mark('new_post')
class NewPostFrame(EditFrame):

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
                                self.e.getall(),
                                self.session.ip,
                                config.BBS_HOST_FULLNAME)
        self.message(u'发表文章成功！')
        self.pause()
        self.goto_back()

@mark('reply_post')
class ReplyPostFrame(EditFrame):

    def initialize(self, boardname, post):
        self.cls()
        self.boardname = boardname
        self.replyid = post['pid']
        title = 'Re: %s' % post['title']
        self.title = self.read_title(prompt=u'请输入标题：',prefix=title)
        super(ReplyPostFrame,self).initialize()

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

    def initialize(self, boardname, post):
        self.cls()
        self.boardname = boardname
        self.pid = post['pid']
        super(EditPostFrame, self).initialize(text=post['content'])
        self.message(u'开始编辑文章')
        
    def finish(self):
        manager.action.update_post(self.boardname,
                                   self.userid,
                                   self.pid,
                                   self.e.getall())
        self.message(u'编辑文章成功！')
        self.pause()
        self.goto_back()

@mark('edit_text')
class EditFileFrame(EditFrame):

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
            self.callback(self.e.get_all_lines())
        else:
            self.callback(self.e.getall())
        self.pause()
        self.goto_back()

    def quit_iter(self):
        self.message(u'放弃本次编辑操作？')
        d = self.readline()
        if not d :
            self.goto_back()

@mark('edit_clipboard')
class EditorClipboardFrame(EditFrame):

    def initialize(self):
        super(EditorClipboardFrame, self).initialize(text=self.get_text())

    def finish(self):
        manager.clipboard.set_clipboard(self.userid, self.e.getall())
        self.message(u'更新暂存档成功！')
        self.pause()
        self.goto_back()

    def get_text(self):
        return self.u(manager.clipboard.get_clipboard(self.userid))
