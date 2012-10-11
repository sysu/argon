from lib import BaseHandler, manager
import tornado.web

class MailHandler(BaseHandler):

    page_size = 10

    def get(self, start = 0):
        userid = self.get_current_user()
        if not userid :
            self.login_page()

        start = int(start) or 0
        total = manager.mail.get_mail_total(userid)

        if start == 0:
            start = total - self.page_size
            if start < 0 :
                start = 0

        maillist = manager.mail.get_mail_simple(userid, start, self.page_size)
        self.write({
                "success":True,
                "content":maillist,
                })

class AjaxAddMailHandler(BaseHandler):

    def get(self):
        self.srender("add_mail")

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
        title=self.get_argument("title", None),
        if not title :
            self.write({
                    "success":False,
                    "content":u"必须有标题！",
                    })
            return
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
        content = fun_gen_quote(mail.owner, mail.content)
        self.write({
                "title": title,
                "content" : content,
                })

    def post(self, mid):
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
        manager.action.reply_mail(userid,
                                  self.get_argument('replymid'),
                                  content=self.get_argument('content'),
                                  title=self.get_argument('title'),
                                  fromaddr=self.request.remote_ip)
        self.write({
                "success":True,
                "content":"回复邮件成功！",
                })
                                 
