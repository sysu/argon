# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import mark
from chaofeng.ui import TextEditor, AppendTable, ColMenu
from model import manager
from argo_frame import ArgoFrame
from libtelnet import zh_format
from datetime import datetime
from editor import EditFrame
from boardlist import ArgoTableFrame
from menu import MenuFrame
from view import ArgoTextBoxFrame
import config

@mark('mail_menu')
class MailMenuFrame(MenuFrame):

    def initialize(self):
        super(MailMenuFrame, self).initialize()
        menu_data = self.get_tidy_data()
        background = self.render_str('menu_mail')
        anim_data = self.get_anim_data()
        self.setup(menu_data, False, 11, background, 0, anim_data)

    def get_tidy_data(self):
        return ColMenu.tidy_data(config.menu['mail'])

    def finish(self):
        self.suspend(self.menu.fetch())

@mark('get_mail')
class GetMailFrame(ArgoTableFrame):

    def setup(self):
        table = self.load(AppendTable, 'mid', start_line=4)
        table.reset_with_upper(self.get_data, self.fformat, 999999999999999)
        super(GetMailFrame, self).setup(table,
                                        config.str['MAIL_QUICK_HELP'],
                                        config.str['MAIL_THEAD'])

    def get_data(self, o, l):
        d = map(lambda x : dict(num=x[0],**x[1]),
                enumerate(manager.action.get_mail(self.userid, o, l)))
        return d

    def fformat(self, d):
        return self.render_str('mail-li', **d)

    def restore(self):
        self.table.reload()   ####  very ugly
        super(GetMailFrame, self).restore()

    def initialize(self):
        super(GetMailFrame, self).initialize()
        self.setup()
        if self.table.is_empty() :
            self.write(u'你没有信笺哟！')
            self.pause()
            self.goto_back()
        self.restore()

    def finish(self):
        mail = self.table.fetch()
        if mail:
            self.suspend('view_mail', mail=mail)

    def show_help(self):
        self.suspend('help',page='mail')

    def get(self, data):
        super(GetMailFrame, self).get(data)
        self.try_action(config.hotkeys['get_mail'].get(data))
        self.table.try_action(config.hotkeys['get_mail_table'].get(data))

    def send_mail(self):
        self.suspend("send_mail")

    def reply(self):
        self.suspend("reply_mail", mail=self.table.fetch())

@mark('send_mail')
class SendMailFrame(EditFrame):

    def readline_s(self, prompt=''):
        self.write(prompt)
        res = self.readline()
        self.write('\r\n')
        return res        

    def initialize(self):
        super(SendMailFrame, self).initialize()
        self.cls()
        self.touserid = self.readline_s(u'收信人：')
        if self.touserid is False:
            self.writeln(u'取消写信！')
            self.pause()
            self.goto_back()
        if not manager.userinfo.get_user(self.touserid):
            self.writeln(u'无法找到该收信人！')
            self.pause()
            self.goto_back()
        self.title = self.readline_s(u'标题:')
        self.setup()
        self.reset()
        self.message(u'发信给 %s' % self.touserid)

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
class ReplyMailFrame(EditFrame):

    def initialize(self, mail):
        super(ReplyMailFrame, self).initialize()
        self.replymail = mail
        self.cls()
        self.touserid = mail['fromuserid']
        self.write(u'标题: ')
        self.title = self.readline(prefix=u'Re: %s'%mail['title'])
        self.setup()
        self.reset()
        self.message(u'回信给 %s' % self.touserid)

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
class ArgoReadMailFrame(ArgoTextBoxFrame):

    def initialize(self, mail):
        super(ArgoReadMailFrame, self).initialize()
        self.setup()
        manager.mail.set_read(self.session.user['uid'], mail['mid'])
        self.set_text(self.render_str('mail-t', **mail))

    def finish(self,e):
        self.goto_back()
