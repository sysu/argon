# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import Frame,EndInterrupt,Timeout
from chaofeng.g import mark,is_chchar
from chaofeng.ui import EastAsiaTextInput,Password,DatePicker,ColMenu,VisableInput,\
    DatePicker, Form
from chaofeng import ascii as ac
from model import manager
from datetime import datetime
from libframe import BaseAuthedFrame, BaseTableFrame, BaseTextBoxFrame
from libframe import chunks
from menu import BaseMenuFrame, NormalMenuFrame
from MySQLdb import DataError
import config

@mark('user_space')
class UserSpaceFrame(NormalMenuFrame):

    def initialize(self):
        super(UserSpaceFrame, self).initialize('user_space')

@mark('user_editdata')
class UserEditDataFrame(BaseAuthedFrame):

    def initialize(self):
        self.cls()
        text = self.render_str('hint/edit_userattr').split('\r\n----\r\n')
        self.form = self.load(Form, [
                ('nickname', text[0], self.handler_nickname),
                ('realname', text[1], self.handler_realname),
                ('email', text[2], self.handler_email),
                ('birthday', text[3], self.handler_birthday),
                ('gender', text[4], self.handler_gender),
                ])
        self.default = default = manager.userinfo.get_user(self.userid)
        default['birthday'] = unicode(default['birthday'].strftime('%Y-%m-%d'))
        default['gender'] = u'1' if default['gender'] else u'0'
        self.form.read(default=default)
        self.writeln(u'全部设置完毕！')
        self.pause()
        self.goto_back()

    def handler_nickname(self, nickname):
        if nickname == self.default['nickname'] :
            return
        if len(nickname) >= 20 :
            raise ValueError(u'昵称太长！')
        manager.userinfo.update_user(self.userid,  nickname=nickname)

    def handler_realname(self, realname):
        if realname == self.default['realname'] :
            return
        if len(realname) >= 20 :
            raise ValueError(u'真实姓名太长！')
        manager.userinfo.update_user(self.userid, realname=realname)

    def handler_email(self, email):
        if email == self.default['email'] :
            return
        if len(email) >= 80 :
            raise ValueError(u'电子邮件过长！')
        manager.userinfo.update_user(self.userid, email=email)

    def handler_birthday(self, birthday):
        if birthday == self.default['birthday'] :
            return
        try: 
            birthday = datetime.strptime(birthday, '%Y-%m-%d')
        except ValueError:
            raise ValueError(u'错误的日期，格式 YYYY-MM-DD')
        manager.userinfo.update_user(self.userid, birthday=birthday)

    def handler_gender(self, gender):
        if not gender or gender == self.default['gender']:
            return
        gender = 0 if gender in ['F', 'f', 'female', 'girl', 'g', '0'] else 1
        manager.userinfo.update_user(self.userid, gender=gender)

@mark('user_nickdata')
class NickDataFrame(BaseMenuFrame):

    nickdata = {
        "shai":u"晒一下",
        "contact":u"联系方式",
        "want":u"想要的东西",
        "job":u"工作",
        "marriage":u"婚恋状况",
        "about":u"个人说明档",
        }

    real, text = zip(*nickdata.items())
    pos = [ (13+i, 10) for i in range(len(real))]
    shortcuts = dict((str(i), i) for i in range(len(real)))
    
    def load_all(self):
        return ((self.real, self.pos, self.shortcuts, self.text), None, '')

    def finish(self):
        a = self.menu.fetch()
        self.suspend('edit_text', filename=a , callback=self.update_user_attr, text=self.user[a] or u'')

    def update_user_attr(self, filename, text):
        self.cls()
        args = {
            filename:text
            }
        try:
            manager.userinfo.update_user(self.userid, **args)
        except None:      ##############  Notice the max buffer len.
            self.write(u'\r\n编辑档案失败！')
        else:
            self.session.user[filename] = text
            self.write(u'\r\n编辑档案成功！')

@mark('user_change_passwd')
class ChangePasswdFrame(BaseAuthedFrame):

    def initialize(self):
        self.write(ac.clear + u'开始修改密码...\r\nCtrl+C退出取消本次活动。')
        self.write(u'\r\n\r\n请输入旧密码进行确认 ：')
        ui_passwd = self.load(Password)
        passwd = ui_passwd.readln()
        if not manager.auth.check_passwd_match(passwd, self.user['passwd']):
            self.write(u'\r\n很抱歉, 您输入的密码不正确。')
            self.pause()
            self.goto_back()
        self.write(u'\r\n请设定新密码：')
        pass1 = ui_passwd.readln()
        self.write(u'\r\n请重新输入新密码以确认:')
        passwd = ui_passwd.readln()
        if pass1 != passwd :
            self.write(u'新密码确认失败, 无法设定新密码。')
            self.pause()
            self.goto_back()
        manager.auth.set_passwd(self.userid, passwd)
        self.write(u'\r\n\r\n密码修改成功！')
        self.pause()
        self.goto_back()

    def get(self,data):
        if data == ac.k_ctrl_c :
            self.goto_back()

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

@mark('user_edit_sign')
class EditSignFrame(BaseTextBoxFrame):

    hotkeys = {
        ac.k_ctrl_e:"set_sign",
        }

    def get_text(self):
        self.signs = manager.usersign.get_all_sign(self.userid)
        return self.render_str('sign-t', signs=self.signs)

    def get_raw_text(self):
        return u'\r\n'.join(self.signs)

    def set_sign(self):
        self.suspend('edit_text', filename=u'签名档', callback=self.save_sign,
                     text=self.get_raw_text(), split=True)

    def save_sign(self, filename, text):
        self.cls()
        if text is None:
            self.write(u'取消设置签名档')
        else:
            data = map(lambda x:u'\r\n'.join(x),
                       chunks(text, 6))
            manager.usersign.set_sign(self.userid, data)
            self.write(u'设置签名档成功！')

    def finish(self, a):
        self.goto_back()        

@mark('query_user')
class QueryUserFrame(BaseTextBoxFrame):

    def initialize(self, userid=None):
        user = manager.query.get_user(self.userid, userid)
        if user :
            self.text = self.render_str('user-t',**user)
            super(QueryUserFrame,self).initialize()
        else:
            self.write(u'\r\n无此id！')
            self.pause()
            self.goto_back()

    def finish(self,a):
        self.goto_back()

    def get_text(self):
        return self.text

@mark('query_user_self')
class QueryUserSelfFrame(BaseTextBoxFrame):

    def initialize(self):
        user = manager.query.get_user(self.userid, self.userid)
        if user :
            self.text = self.render_str('user_self-t', **user)
            super(QueryUserSelfFrame, self).initialize()
        else:
            self.goto_back()

    def finish(self,a):
        self.goto_back()

    def get_text(self):
        return self.text

@mark('query_user_iter')
class QueryUserIterFrame(QueryUserFrame):

    def initialize(self):
        self.write(ac.clear + u'要查询谁？')
        userid = self.readline(acceptable=ac.is_alnum)
        if userid :
            super(QueryUserIterFrame,self).initialize(userid)
        else:
            self.write(u'\r\n取消查询！')
            self.pause()
            self.goto_back()

    def query_user_normal(self, userid):
        user = manager.userinfo.get_user(userid)
        if user is None :
            self.write(u'没有该用户！')
            self.pause()
            self.goto_back()
        else:
            return user

@mark('test_keyboard')
class TestKeyBoardFrame(BaseAuthedFrame):

    all_test_key = [
        "Cursor Up", "Cursor Down", "Cursor Left", "Cursor Right",
        ]

    def initialize(self):
        self.cls()
        self.render('hint/test_keyboard')
        self.title = self.readline(prompt=u'请输入简要的按键方案说明：')
        if not self.title :
            self.write(u'放弃操作')
            self.pause()
            self.goto_back()
        self.test_all()

    def get_key(self):
        buf = []
        while True :
            char = self.read_secret()
            if char in ac.ks_finish:
                break
            buf.append(char)
        return ''.join(buf)

    def test_all(self):
        buf = [u'来自 [#1;31%%]%s[%%#] 的按键测试\r\n\r\n' % self.userid]
        res = {}
        self.write('r\n----------\r\n\r\n')
        for key in self.all_test_key :
            self.write(u'开始测试... [%s] ' % key)
            res[key] = self.get_key()
            self.writeln(u'  结果 %r' % res[key])
            buf.append(u'    测试 %-15s 的结果为 %r  \r\n' % (key, self.s(res[key])))
        self.goto('edit_text', filename='Test KeyBoard', callback=self.publish_as_post,
                  text=''.join(buf))

    def publish_as_post(self, filename, text):
        manager.action.new_post('Test',
                                self.userid,
                                u'[按键测试] %s ' % self.title,
                                text,
                                self.session.ip,
                                config.BBS_HOST_FULLNAME,
                                replyable=False)
