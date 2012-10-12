#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib import BaseHandler, manager, url_for_avatar, timeformat, fun_gen_quote
import tornado.web

class MailHandler(BaseHandler):

    def get(self):
        self.srender('mail.html')

class AjaxMailListHandler(BaseHandler):

    page_size = 20

    def get(self, start = None):
        userid = self.get_current_user()
        if not userid :
            self.write({
                    "success": False,
                    "content": "未认证用户！",
                    })
            return

        total = manager.mail.get_mail_total(userid)
        if start is None:
            start = manager.mail.get_first_unread(userid)
            if start == 0 :
                start = total
            start = start // 20 * 20
        else:
            start = int(start) 

        if start > total:
            self.write({
                    "success": False,
                    "content": "没有新的数据！",
                    })
            return

        if (start < 0) :
            start = total - self.page_size
            if start < 0 :
                start = 0

        maillist = manager.mail.get_mail_simple(userid, start, self.page_size)
        for li in maillist :
            li['sendtime'] = timeformat(li['sendtime'])
        self.write({
                "success": True,
                "content": maillist,
                "start": start,
                })

class AjaxAddMailHandler(BaseHandler):

    def get(self):
        self.render('addmail.html')

    def post(self):
        userid = self.get_current_user()
        if not userid :
            self.login_page()
            return
        touserid = manager.userinfo.safe_userid(self.get_argument("touserid"))
        if not touserid :
            self.write({
                    "success":False,
                    "content":u"错误的收件人。",
                    })
            return
        title = self.get_argument("title", None)
        if not title :
            self.write({
                    "success":False,
                    "content":u"必须有标题！",
                    })
            return
        signnum = self.get_argument('signnum', None)
        if signnum is None or signnum < manager.usersign.get_sign_num(userid):
            signature = ''
        else:
            signature = manager.usersign.get_sign(userid, signnum)
        manager.action.send_mail(
            fromuserid=userid, touserid=touserid,
            content=self.get_argument("text"), title=title, 
            fromaddr=self.request.remote_ip, signature=signature
            )
        self.write({
                "success":True,
                "content":"发送邮件成功！",
                })

class AjaxReplyMailHandler(BaseHandler):

    def get(self, mid):
        userid = self.get_current_user()
        if not userid :
            self.login_page()
            return
        mail = manager.mail.one_mail(mid)
        if not mail or mail.touserid != userid :
            self.write({
                    "success":False,
                    "content":"没有该邮件！",
                    })
            return
        title = mail.title if mail.title.startswith('Re: ') \
            else 'Re: %s' % mail.title
        content = fun_gen_quote(mail.fromuserid, mail.content)
        self.render('replymail.html', title=title, content=content, mid=mid)

    def post(self, mid):
        userid = self.get_current_user()
        if not userid :
            self.write({
                    "success": False,
                    "content": "未认证用户！",
                    })
            return
        mail = manager.mail.one_mail(mid)
        if not mail or mail.touserid != userid :
            self.write({
                    "success":False,
                    "content":"没有该邮件！",
                    })
            return
        signnum = self.get_argument('signnum', None)
        if signnum is None or signnum < manager.usersign.get_sign_num(userid):
            signature = ''
        else:
            signature = manager.usersign.get_sign(userid, signnum)
        manager.action.reply_mail(userid, mail, 
                                  content=self.get_argument('content'),
                                  title=self.get_argument('title'),
                                  fromaddr=self.request.remote_ip,
                                  signature=signature)
        self.write({
                "success":True,
                "content":"回复邮件成功！",
                })

class AjaxGetMailHandler(BaseHandler):

    def get(self, mid):
        userid = self.get_current_user()
        if not userid :
            self.write({
                    "success":False,
                    "content":"没有登录",
                    })
            return
        mail = manager.mail.one_mail(mid)
        if mail and (mail.touserid == userid):
            manager.mail.set_mail_read(mid)
            self.write({
                    "success":True,
                    "UserAvatar": url_for_avatar(mail.fromuserid),
                    "Title": mail.title,
                    "Userid": mail.fromuserid,
                    "Content": mail.content,
                    "Sendtime": timeformat(mail.sendtime),
                    "Signature": mail.signature,
                    "Mid": mail.mid,
                    })
            return
        self.write({
                "success":False,
                "content":"没有该邮件！",
                })
