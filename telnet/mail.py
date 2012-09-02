#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import mark
from chaofeng.ui import TextEditor, ColMenu
from model import manager
from datetime import datetime
from libframe import BaseTableFrame, BaseTextBoxFrame, \
    BaseEditFrame, gen_quote_mail, wrapper_index
from menu import NormalMenuFrame
from libformat import style_to_etelnet, etelnet_to_style
import config
import random

@mark('mail_menu')
class MailMenuFrame(NormalMenuFrame):

    def initialize(self):
        super(MailMenuFrame, self).initialize('mail')

@mark('get_mail')
class GetMailFrame(BaseTableFrame):

    def quick_help(self):
        self.writeln(config.str['MAIL_QUICK_HELP'])

    def print_thead(self):
        self.writeln(config.str['MAIL_THEAD'])

    def notify(self, msg):
        self.write(ac.move2(0, 1))
        self.render('top_msg', messages=msg)
        self.table.restore_cursor_gently()

    def get_default_index(self):
        return self.default

    def get_data(self, start, limit):
        res = manager.action.get_mail(self.userid, start, limit,
                                      touid=self.session.user['uid'])
        return wrapper_index(res, start)

    def get_total(self):
        return manager.mail.get_mail_total(self.uid, self.userid)

    def wrapper_li(self, d):
        return self.render_str('mail-li', **d)

    def catch_nodata(self, e):
        self.write(u'你没有信笺哟！')
        self.pause()
        self.goto_back()

    def initialize(self, default=None):
        manager.notify.clear_mail_notify(self.userid)
        self.uid = self.session.user['uid']
        if default is None:
            default = self.get_total()
        self.default = default
        super(GetMailFrame, self).initialize()
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
            self.goto('view_mail', mail=mail)

    def send_mail(self):
        self.suspend("send_mail")

    def reply(self):
        self.suspend("reply_mail", mail=self.table.fetch())

class MailReadAttrsMixIn:

    prompt = u'[1;32m0[m~[1;32m%s[m/[1;32mx[m  选择/随机签名档 [1;32mt[m标题，[1;32mq[m取消：'
    
    def update_attr(self, attrs):
        self.write(''.join([ac.move2(21, 1),
                            ac.clear1,
                            self.render_str('edit_head_email', **attrs)]))

    def read_attrs(self):
        sign_num = manager.usersign.get_sign_num(self.userid)
        attrs = {
            "touserid":self.touserid, 
            "usesign":0,
            "title":u"[正在设定标题]",
            }
        if sign_num :
            attrs["usersign"] = random.randint(1, sign_num)
        self.update_attr(attrs)
        attrs['title'] = self.readline_safe(prompt=u'标题：', buf_size=40)
        if not attrs['title']:
            return
        prompt = ''.join([ac.move2(25, 1), ac.kill_line,
                          self.prompt % sign_num])
        while True:
            op = self.readline_safe(buf_size=4, prompt=prompt)
            if op == '':
                break
            elif op is False or op=='q':
                return 
            elif op == 't':
                attrs['title'] = self.readline_safe(prompt=u'\r\x1b[K标题：',
                                                    prefix=attrs['title'],
                                                    buf_size=40)
                if not attrs['title']:
                    return
            elif op == 'x' and sign_num:
                attrs['usersign'] = random.randint(1, sign_num)
            elif op.isdigit():
                n = int(op)
                if n <= sign_num:
                    attrs['usersign'] = n
            self.update_attr[attrs]
        return attrs

@mark('send_mail')
class SendMailFrame(BaseEditFrame, MailReadAttrsMixIn):

    def initialize(self, touserid=None):
        self.cls()
        if touserid is None:
            touserid = self.readline_safe(prompt=u'收信人：')
        if touserid is False :
            self.writeln(u'取消写信！')
            self.pause()
            self.goto_back()
        if not manager.userinfo.get_user(touserid):
            self.writeln(u'无法找到该收信人！')
            self.pause()
            self.goto_back()
        self.touserid = touserid
        self.attrs = self.read_attrs()
        if not self.attrs:
            self.goto_back()
        super(SendMailFrame, self).initialize()

    def finish(self):
        if self.attrs['usesign'] :
            signtext = manager.usersign.get_sign(self.userid,
                                                 self.attrs['usesign']-1)
        else:
            signtext = ''
        mid = manager.action.send_mail(
            fromuserid=self.userid,
            touserid=self.touserid,
            content=etelnet_to_style(self.e.fetch_all()),
            title=self.attrs['title'],
            fromaddr=self.session.ip,
            signature=signtext)
        self.goto_back()

@mark("reply_mail")
class ReplyMailFrame(BaseEditFrame, MailReadAttrsMixIn):

    def initialize(self, mail):
        self.replymail = mail
        self.cls()
        self.touserid = mail['fromuserid']
        if not manager.userinfo.get_user(self.touserid):
            self.writeln(u'无法找到该收信人！')
            self.pause()
            self.goto_back()
        self.attrs = self.read_attrs()
        if not self.attrs :
            self.goto_back()
        text = gen_quote_mail(mail)
        super(ReplyMailFrame, self).initialize(text=style_to_etelnet(text))

    def finish(self):
        if self.attrs['usesign'] :
            signtext = manager.usersign.get_sign(self.userid,
                                                 self.attrs['usesign']-1)
        else:
            signtext = ''
        manager.action.reply_mail(self.userid,
                                  self.replymail,
                                  content=etelnet_to_style(self.e.fetch_all()),
                                  title=self.attrs['title'],
                                  fromaddr=self.session.ip,
                                  signature=signtext)
        self.goto_back()

@mark('view_mail')
class ReadMailFrame(BaseTextBoxFrame):

    hotkeys = {
        "r":"reply",
        "R":"reply",
        }

    def get_text(self):
        return self.render_str('mail-t', **self.mail)

    def initialize(self, mail):
        self.mail = mail
        manager.mail.set_read(self.session.user['uid'], mail['mid'])
        super(ReadMailFrame, self).initialize()

    def goto_back(self):
        self.goto('get_mail', default=manager.mail.get_rank(
                self.userid,
                self.session.user['uid'],
                self.mail['mid']))

    def finish(self,e):
        if e is True:
            mail = manager.mail.next_mail(
                    self.userid,
                    self.session.user['uid'],
                    self.mail['mid'])
            if mail :
                self.goto('view_mail', mail=mail)
        elif e is False:
            mail = manager.mail.prev_mail(
                    self.userid,
                    self.session.user['uid'],
                    self.mail['mid'])
            if mail:
                self.goto('view_mail', mail=mail)
        self.goto_back()

    def reply(self):
        self.suspend('reply_mail', mail=self.mail)
