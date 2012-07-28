# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import mark
from chaofeng.ui import TextEditor, ColMenu
from model import manager
from datetime import datetime
from libframe import BaseTableFrame, BaseTextBoxFrame, BaseEditFrame
from menu import NormalMenuFrame
import config

@mark('mail_menu')
class MailMenuFrame(NormalMenuFrame):

    def initialize(self):
        super(MailMenuFrame, self).initialize('mail')

@mark('get_mail')
class GetMailFrame(BaseTableFrame):

    def top_bar(self):
        self.writeln(self.render_str('top'))

    def quick_help(self):
        self.writeln(config.str['MAIL_QUICK_HELP'])

    def print_thead(self):
        self.writeln(config.str['MAIL_THEAD'])

    def notify(self, msg):
        self.write(ac.move2(0, 1))
        self.render('top_msg', messages=msg)
        self.table.restore_cursor_gently()

    def get_default_index(self):
        return 0

    def get_data(self, start, limit):
        return manager.action.get_mail(self.userid, start, limit)

    def wrapper_li(self, d):
        return self.render_str('mail-li', **d)

    def initialize(self):
        super(GetMailFrame, self).initialize()
        if self.table.is_empty() :
            self.write(u'你没有信笺哟！')
            self.pause()
            self.goto_back()
        self.restore()

    def get(self, data):
        if data in ac.ks_finish:
            self.finish()
        self.table.do_command(config.hotkeys['g_table'].get(data))
        self.table.do_command(config.hotkeys['maillist_table'].get(data))
        self.do_command(config.hotkeys['maillist'].get(data))

    def finish(self):
        mail = self.table.fetch()
        if mail:
            self.suspend('view_mail', mail=mail)

    def send_mail(self):
        self.suspend("send_mail")

    def reply(self):
        self.suspend("reply_mail", mail=self.table.fetch())

@mark('send_mail')
class SendMailFrame(BaseEditFrame):

    def initialize(self):
        self.cls()
        touserid = self.read_title(prompt=u'收信人：')
        if touserid is False :
            self.writeln(u'取消写信！')
            self.pause()
            self.goto_back()
        if not manager.userinfo.get_user(touserid):
            self.writeln(u'无法找到该收信人！')
            self.pause()
            self.goto_back()
        self.touserid = touserid
        self.writeln()
        self.title = self.readline(prompt=u'标题:')
        if self.title :
            super(SendMailFrame, self).initialize()
            self.message(u'发信给 %s' % self.touserid)
        else:
            self.message(u'放弃发表新文章')

    def finish(self):
        manager.action.send_mail(fromuserid=self.userid,
                                 touserid=self.touserid,
                                 content=self.e.getall(),
                                 title=self.title,
                                 fromaddr=self.session.ip)
        self.message(u'发送成功！')
        self.pause()
        self.goto_back()

@mark("reply_mail")
class ReplyMailFrame(BaseEditFrame):

    def initialize(self, mail):
        self.replymail = mail
        self.cls()
        self.touserid = mail['fromuserid']
        self.write(u'标题: ')
        self.title = self.readline(prefix=u'Re: %s'%mail['title'])
        if self.title :
            super(ReplyMailFrame, self).initialize()
            self.message(u'回信给 %s' % self.touserid)
        else:
            self.write(u'放弃编辑')
            self.pause()
            self.goto_back()

    def finish(self):
        manager.action.reply_mail(self.userid,
                                  self.replymail,
                                  content=self.e.getall(),
                                  title=self.title,
                                  fromaddr=self.session.ip)
        manager.mail.set_reply(self.session.user['uid'], self.replymail['mid'])
        self.message(u'回复成功！')
        self.pause()
        self.goto_back()

@mark('view_mail')
class ReadMailFrame(BaseTextBoxFrame):

    def get_text(self):
        return self.render_str('mail-t', **self.mail)

    def initialize(self, mail):
        self.mail = mail
        manager.mail.set_read(self.session.user['uid'], mail['mid'])
        super(ReadMailFrame, self).initialize()

    def finish(self,e):
        self.goto_back()
