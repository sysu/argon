#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

import logging
logger = logging.getLogger('@mail')

from chaofeng import ascii as ac
from chaofeng.g import mark
from edit import BaseEditFrame, handler_edit
from chaofeng.ui import NullValueError, FinitePagedTable
from libframe import BaseAuthedFrame, gen_quote_mail
from view import BaseTextBoxFrame
from model import manager
import config
import random

@mark('mail_menu')
class MailMenuFrame(BaseAuthedFrame):

    def initialize(self):
        self.goto('menu', 'mail')

class BaseMailListFrame(BaseAuthedFrame):

    _TABEL_START_LINE = 4
    _TABEL_HEIGHT = 20

    def get(self, char):
        if char == ac.k_finish:
            self.fetch_mail('next_frame')
        self.do_command(self.shortcuts.get(char))
        self._table.do_command(self.shortcuts_table.get(char))
        self.fetch_mail(self.shortcuts_fetch.get(char))
        self.fetch_mail_update(self.shortcuts_update.get(char))

    def _wrapper_li(self, d):
        return self.render_str('mail-li', **d)

    def catch_nodata(self):
        self.cls()
        self.pause_back(u'你没有信笺哟！')

    def _init_screen(self):
        self.cls()
        self.top_bar()
        self.push('\r\n')
        self.push(config.str['MAILLIST_QUICK_HELP'])
        self.push('\r\n')
        self.push(config.str['MAILLIST_THEAD'])
        self.bottom_bar()
        self._table.restore_screen()

    def setup(self, dataloader, counter, default=0):
        try:
            self._table = self.load(FinitePagedTable, dataloader,
                                    self._wrapper_li, counter, default,
                                    start_line=self._TABEL_START_LINE,
                                    height=self._TABEL_HEIGHT)
        except NullValueError:
            self.catch_nodata()
            raise NullValueError
        self._init_screen()

    def fetch_mail(self, cmd):
        if cmd is None:
            return
        mail = self._table.fetch()
        getattr(self, cmd)(mail)

    def fetch_mail_update(self, cmd):
        if cmd is None:
            return
        mail = self._table.fetch()
        mail = getattr(self, cmd)(mail)
        if mail is not None:
            self._table.set_hover_data(mail)

    def reload(self):
        self._table.reload()
        self._table.restore_screen()

    def restore(self):
        self._init_screen()

@mark('get_mail')
class ReadMailFrame(BaseMailListFrame):

    shortcuts = {
        ac.k_ctrl_p:"send_mail",
        ac.k_left:"goto_back",
        'p':'same_topic_mode',
        ac.k_ctrl_s:'same_topic_mode',
        }
    shortcuts_table = {
        ac.k_up:"move_up",
        ac.k_down:"move_down",
        ac.k_page_up:"page_up",
        ac.k_page_down:"page_down",
        " ":"page_down",
        "k":"move_up",       "p":"move_up",      
        "j":"movewn",     "n":"movewn",
        "P":"page_up",       "N":"pagewn",
        "$":"goto_last",
        ac.k_home:"goto_first",
        ac.k_end:"goto_last",
        }
    shortcuts_fetch = {
        ac.k_right : "next_frame",
        'r':'reply',
        'R':'reply',
        'd':'remove_mail',
        'D':'remove_mail_range',
        ac.k_ctrl_c:'repost',
        }
    shortcuts_update = {
        'm':'set_m_mark',
        }

    NORMAL_MODE = 0
    TOPICE_MODE = 1

    MODE_LOADER = [
        manager.mail.get_mail_loader,
        manager.mail.get_topic_mail_loader,
        ]

    MODE_COUNTER = [
        manager.mail.get_mail_counter,
        manager.mail.get_mail_counter,
        ]

    MODE_RANKER = [
        manager.mail.get_mid_rank,
        manager.mail.get_topic_mid_rank,
        ]

    def get_mid_rank(self, mid):
        return self.MODE_RANKER[self.mode](self.session.user['uid'],
                                           self.userid,
                                           mid)

    def initialize(self, mode=0):
        manager.status.set_status(self.seid,
                                  manager.status.MAIL)
        manager.notify.clear_mail_notify(self.userid)
        self.uid = self.session.user['uid']
        self.mode = mode
        dataloader, counter = self._get_loader(mode)
        self.setup(dataloader, counter)

    def _get_loader(self, mode):
        return (self.MODE_LOADER[mode](self.uid, self.userid),
                self.MODE_COUNTER[mode](self.uid, self.userid))

    def reset_mode(self, mode):
        dataloader, counter = self._get_loader(mode)
        try:
            self._table.reset_load(dataloader, counter, 0)
        except NullValueError:
            return
        self.get_mid_rank = self.MODE_RANKER[mode]
        self._init_screen()

    def change_mode(self):
        self.mode = 1 - self.mode
        self.reset_mode(self.mode)

    def next_frame(self, mail):
        self.suspend('_view_mail_o', mail=mail)

    def send_mail(self):
        self.suspend('send_mail')

    def reply(self, mail):
        self.suspend('_reply_mail_o', mail=mail)

    def set_m_mark(self, mail):
        return manager.mail.set_m_mark(self.session.user.uid,
                                       mail)

    def remove_mail(self, mail):
        if self.bottom_do(self.confirm, prompt=u'删除你的文章？[y/n] ') :
            manager.mail.remove_mail(self.session.user.uid,
                                     mail['mid'])
            self.reload()

    def remove_mail_range(self):
        start = self.readline(prompt=u'首篇文章编号： ')
        if start.isdigit():
            end = self.readline(prompt=u'末篇文章编号：')
            if end.isdigit() :
                start_mid = manager.mail.index2mid(self.session.user.uid,
                                                   int(start) - 1)
                end_mid = manager.mail.index2mid(self.session.user.uid,
                                                 int(end) - 1)
                if start_mid >= end_mid :
                    return
                manager.mail.remove_mail_range(self.session.user.uid,
                                               self.userid,
                                               start_mid, end_mid)
                self.reload()

    def restore(self):
        if self.session['lastmid'] and\
                self.session['lastmid'] != self._table.fetch()['mid']:
            default = self.get_mid_rank(self.session['lastmid'])
        elif not self.session:
            default = 0
        else:
            default = self._table.fetch_num()
        try:
            try:
                self._table.setup(default)
            except NullValueError:
                self._table.setup(0)
        except NullValueError:
            self.catch_nodata()
            raise ValueError
        self._init_screen()

@mark('send_mail')
class SendMailFrame(BaseAuthedFrame):

    shortcuts = {
        ac.k_ctrl_w : "finish",
        }
    shortcuts_ui = config.shortcuts['edit_ui']

    PROMPT = u'[25;1H[K[1;32m0[m~[1;32m%s[m/[1;32mx[m  选择/随机签名档 [1;32mt[m标题，[1;32mq[m取消：'
    
    def update_attr(self, attrs):
        self.render('edit_head_email', **attrs)

    def read_attrs(self, touserid, sign_num):
        attrs = {
            "touserid":touserid, 
            "usesign":0,
            "title":u"[正在设定标题]",
            }
        if sign_num :
            attrs["usersign"] = random.randint(1, sign_num)
        self.update_attr(attrs)
        attrs['title'] = self.safe_readline(prompt=u'标题：', buf_size=40)
        if not attrs['title']:
            return
        prompt = self.PROMPT % sign_num
        while True:
            self.update_attr(attrs)
            op = self.safe_readline(buf_size=4, prompt=prompt)
            if op == '':
                break
            elif op is False or op=='q':
                return 
            elif op == 't':
                attrs['title'] = self.safe_readline(prompt=u'\r\x1b[K标题：',
                                                    buf_size=40)
                if not attrs['title']:
                    return
            elif op == 'x' and sign_num:
                attrs['usesign'] = random.randint(1, sign_num)
            elif op.isdigit():
                n = int(op)
                if n <= sign_num:
                    attrs['usesign'] = n
        return attrs

    def initialize(self, touserid=None):
        manager.status.set_status(self.seid,
                                  manager.status.SMAIL)
        self.cls()
        if touserid is None:
            touserid = self.safe_readline(prompt=u'收信人：')
        if touserid is False :
            self.writeln(u'取消写信！')
            self.pause()
            self.goto_back()
        if not manager.userinfo.get_user(touserid):
            self.writeln(u'无法找到该收信人！')
            self.pause()
            self.goto_back()
        self.touserid = touserid
        sign_num = manager.usersign.get_sign_num(self.userid)
        self.attrs = self.read_attrs(touserid, sign_num)
        if not self.attrs:
            self.goto_back()
        self.suspend('edit_text', filename='mail')

    @handler_edit
    def restore(self):
        pass

    def handler_mail(self, text):
        if self.attrs['usesign'] :
            signtext = manager.usersign.get_sign(self.userid,
                                                 self.attrs['usesign']-1)
        else:
            signtext = ''
        mid = manager.action.send_mail(
            fromuserid=self.userid,
            touserid=self.touserid,
            content=text,
            title=self.attrs['title'],
            fromaddr=self.session.ip,
            signature=signtext)
        self.goto_back()

@mark("_reply_mail_o")
class ReplyMailFrame(BaseEditFrame):

    PROMPT = u'[25;1H[K[1;32m0[m~[1;32m%s[m/[1;32mx[m  选择/随机签名档 [1;32mt[m标题，[1;32mq[m取消：'
    
    def update_attr(self, attrs):
        self.render('edit_head_email', **attrs)

    def read_attrs(self, touserid, sign_num, title):
        attrs = {
            "touserid":touserid, 
            "usesign":0,
            "title":title
            }
        if sign_num :
            attrs["usersign"] = random.randint(1, sign_num)
        prompt = self.PROMPT % sign_num
        while True:
            self.update_attr(attrs)
            op = self.safe_readline(buf_size=4, prompt=prompt)
            if op == '':
                break
            elif op is False or op=='q':
                return 
            elif op == 't':
                attrs['title'] = self.safe_readline(prompt=u'\r\x1b[K标题：',
                                                    prefix=u'Re: ',
                                                    buf_size=40)
                if not attrs['title']:
                    return
            elif op == 'x' and sign_num:
                attrs['usesign'] = random.randint(1, sign_num)
            elif op.isdigit():
                n = int(op)
                if n <= sign_num:
                    attrs['usesign'] = n
        return attrs

    def initialize(self, mail):
        manager.status.set_status(self.seid,
                                  manager.status.RMAIL)
        self.replymail = mail
        self.cls()
        self.touserid = mail['fromuserid']
        if not manager.userinfo.get_user(self.touserid):
            self.writeln(u'无法找到该收信人！')
            self.pause()
            self.goto_back()
        sign_num = manager.usersign.get_sign_num(self.userid)
        title = mail['title'] if mail['title'].startswith('Re:')\
            else u'Re: %s' % mail['title']
        self.attrs = self.read_attrs(self.touserid, sign_num, title=title)
        if not self.attrs :
            self.goto_back()
        text = gen_quote_mail(mail)
        self.suspend('edit_text', filename='mail', text=text)

    @handler_edit
    def restore(self):
        self.goto_back()

    def handler_mail(self, text):
        if self.attrs['usesign'] :
            signtext = manager.usersign.get_sign(self.userid,
                                                 self.attrs['usesign']-1)
        else:
            signtext = ''
        manager.action.reply_mail(self.userid,
                                  self.replymail,
                                  content=text,
                                  title=self.attrs['title'],
                                  fromaddr=self.session.ip,
                                  signature=signtext)

@mark('_view_mail_o')
class ReadMailFrame(BaseTextBoxFrame):

    shortcuts = {
        "r":"reply",
        "R":"reply",
        ac.k_ctrl_x:"change_mode",
        ac.k_left:"back_to_maillist",
        }
    MODE_LOADER = [
        manager.mail.get_mail_loader_signle,
        manager.mail.get_topic_loader_signle,
        ]
    MODE_BOTTOM = [
        'bottom_view',
        'bottom_view_topic',
        ]

    def wrapper_mail(self, mail):
        return self.render_str('mail-t', **mail)

    def initialize(self, mail, mode=0):
        manager.status.set_status(self.seid,
                                  manager.status.RMAIL)
        manager.mail.set_read(self.session.user['uid'], mail['mid'])
        self.mail = mail
        self.mode = mode
        self._set_mode(mode)
        self.setup(self.wrapper_mail(mail))

    def _set_mode(self, mode):
        self.next_loader, self.prev_loader = self.MODE_LOADER[mode](
            self.session.user.uid,
            self.userid
            )
        self.bottom_tpl = self.MODE_BOTTOM[mode]

    def change_mode(self):
        self.mode = 1 - self.mode
        self._set_mode(self.mode)
        self.restore_screen()

    def bottom_bar(self, s, l, message=''):
        self.push(ac.move2(24, 1))
        self.render(self.bottom_tpl, s=s, l=l, message=message)

    def finish(self, e=None):
        logger.debug('finish [%s]', e)
        if e is None:
            self.session['lastmid'] = self.mail['mid']
            self.goto_back()
        if e is True:
            mail = self.next_loader(self.mail['mid'])
        else:
            mail = self.prev_loader(self.mail['mid'])
        if not mail:
            self.session['lastmid'] = self.mail['mid']
            self.goto_back()
        self.mail = mail
        self.reset_text(self.wrapper_mail(self.mail), 0)

    def reply(self):
        self.suspend('_reply_mail_o', mail=self.mail)

    def back_to_maillist(self):
        self.session['lastmid'] = self.mail['mid']
        self.goto_back_history('get_mail')
