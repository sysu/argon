# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import Frame,EndInterrupt,Timeout
from chaofeng.g import mark,is_chchar
from chaofeng.ui import EastAsiaTextInput,Password,DatePicker,Form,ColMenu,VisableInput
from chaofeng import ascii as ac
from model import manager
from datetime import datetime
from argo_frame import AuthedFrame
from menu import NormalMenuFrame
from view import TextBoxFrame
from MySQLdb import DataError
import config

@mark('user_space')
class UserSpaceFrame(NormalMenuFrame):

    def initialize(self):
        super(UserSpaceFrame, self).initialize('user_space')

@mark('user_editdata')
class UserEditDataFrame(AuthedFrame):

    def initialize(self):
        self.cls()
        self.render('edit_user_data')
        user = self.session.user
        buf = [user.nickname, user.realname,
               user.address, user.email,
               user.birthday.strftime("%Y-%m-%d"),
               'M' if user.gender else 'F']
        form = self.load(Form, buf, [
                self.load(EastAsiaTextInput), 
                self.load(EastAsiaTextInput),
                self.load(EastAsiaTextInput),
                self.load(EastAsiaTextInput),
                self.load(DatePicker),
                self.load(VisableInput),
                ], 4, 24)
        form.restore_screen()
        data = form.read()
        if data is False:
            self.write(u'\r\n取消编辑！')
            self.pause()
            self.goto_back()
        self.write(u'\r\n\r\n确认修改您的资料？y/else.')
        d = self.readline()
        if d == 'y' :
            self.set_user_attr(*data)
            self.write(u'\r\n修改成功!')
        else:
            self.write(u'\r\n取消编辑')
        self.pause()
        self.goto_back()

    def set_user_attr(self, nickname, realname, address, email, birthday, gender):
        gender = 0 if gender in 'Ff' else 1
        packup = dict(nickname=nickname, realname=realname, address=address,
                      email=email, birthday=birthday, gender=gender)
        manager.userinfo.update_user(self.userid, **packup)
        self.session.user.update(packup)

@mark('user_nickdata')
class NickDataFrame(AuthedFrame):

    options = ('shai','contact','want','job','marriage','about')
    def initialize(self):
        self.cls()
        self.render('nickdata')
        res = self.select(lambda o : self.write(ac.move2(12,1)+ ac.clear1+
                                                unicode(self.session.user[o])+
                                                ac.move2(10,6) + ac.kill_to_end +
                                                config.user_setting['nickdata'][o]),
                          self.options)
        if res is not False:
            self.sel = self.options[res]
            self.suspend('edit_text', callback=self.save_text,
                         filename=config.user_setting['nickdata'][self.sel])
        else:
            self.write(u'\r\n取消设置！')
            self.pause()
            self.goto_back()

    def save_text(self, text):
        self.text = text

    def restore(self):  ################ Ugly
        self.cls()
        if self.text is None :
            self.write(u'\r\n取消设置资料')
        else:
            args = {
                self.sel : self.text,
                }
            try:
                manager.userinfo.update_user(self.userid,  **args)
            except:
                self.write(u'\r\n编辑档案失败！')
            else:
                self.session.user[self.sel] = self.text
                self.write(u'\r\n编辑档案成功！')
        self.pause()
        self.goto_back()

@mark('user_change_passwd')
class ChangePasswdFrame(AuthedFrame):

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
        ui_passwd.reset()
        pass1 = ui_passwd.readln()
        self.write(u'\r\n请重新输入新密码以确认:')
        ui_passwd.reset()
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
class EditSignFrame(AuthedFrame):

    def initialize(self):
        self.cls()
        self.render('edit_sign')
        signs = manager.usersign.get_all_sign(self.userid)
        r = self.select(lambda o : self.render('sign-li',index=o[0],content=o[1]),
                        tuple(enumerate(signs)))
        if r is False:
            self.write(u'取消设置签名档')
            self.pause()
            self.goto_back()
        text = '\r\n'.join(signs)
        self.suspend('edit_text', filename=u'签名档', callback=self.save_text, text=text, l=r*6, split=True)

    def save_text(self, text):
        self.text = text

    def restore(self):
        self.cls()
        if self.text is None:
            self.write(u'取消设置签名档')
            self.goto_back()
        data = map(lambda x:'\r\n'.join(x),
                   chunks(self.text, 6))
        manager.usersign.set_sign(self.userid, data)
        self.write(u'设置签名档成功！')
        self.pause()
        self.goto_back()

@mark('query_user')
class QueryUserFrame(TextBoxFrame):

    def initialize(self, userid=None):
        if userid is None:
            userid = self.userid
        self.query_user_normal(userid)
        super(QueryUserFrame,self).initialize()

    def query_user_normal(self, userid):
        user = manager.userinfo.get_user(userid)
        if user is None :
            self.write(u'没有该用户！')
            self.pause()
            self.goto_back()
        else:
            self.query_user = user
            self.text = self.render_str('user-t',**user)

    def finish(self,a):
        self.goto_back()

    def get_text(self):
        return self.text

@mark('query_user_iter')
class QueryUserIterFrame(QueryUserFrame):

    def initialize(self):
        self.write(ac.clear + u'要查询谁？')
        userid = self.readline(acceptable=ac.is_alnum)
        print repr(userid)
        super(QueryUserIterFrame,self).initialize(userid)

