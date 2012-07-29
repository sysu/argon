# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import Frame,EndInterrupt,Timeout
from chaofeng.g import mark,is_chchar
from chaofeng.ui import EastAsiaTextInput,Password,DatePicker,ColMenu,VisableInput,\
    DatePicker
from chaofeng import ascii as ac
from model import manager
from datetime import datetime
from libframe import BaseAuthedFrame, BaseTableFrame, BaseFormFrame, BaseTextBoxFrame
from libframe import chunks
from menu import BaseMenuFrame, NormalMenuFrame
from MySQLdb import DataError
import config

@mark('user_space')
class UserSpaceFrame(NormalMenuFrame):

    def initialize(self):
        super(UserSpaceFrame, self).initialize('user_space')

@mark('user_editdata')
class UserEditDataFrame(BaseFormFrame):

    attr = ['nickname', 'realname', 'email', 'birthday', 'gender']
    attrzh = [u'昵称', u'真实姓名', u'电子邮箱', u'生日', u'性别']

    nickstr = [ lambda x : x, lambda x : x, lambda x : x,
                lambda x : x.strftime(u'%Y-%m-%d'),
                lambda x : u'M' if x else u'F']

    inputers = [ lambda x: x.readline(prompt=u'输入昵称： ',
                                      acceptable=ac.isalpha,
                                      prefix=x.form['nickname']),
                 lambda x: x.readline(prompt=u'输入真实姓名： ',
                                      prefix=x.form['realname']),
                 lambda x: x.readline(prompt=u'输入电子邮箱： ',
                                      prefix=x.form['email']),
                 lambda x: x.read_date(),
                 lambda x: x.read_gender(),
                 ]

    def read_gender(self):
        d = self.readline(prompt=u'输入性别(Male/Female)： ',
                          acceptable=lambda x: x in u'MF',
                          buf_size=1,
                          prefix=u'M' if self.form['gender'] else u'F')
        return 0 if d=='F' else 1        
                          
    def read_date(self):
        d = self.read_lbd(lambda : self.load(DatePicker).set_from_date(self.form["birthday"]).\
                              read(prompt=u"请输入生日(xxxx-xx-xx)"))
        return d or self.form['birthday']
    
    def get_data_len(self):
        return len(self.attr)        
    
    def get_data_index(self, index):
        value = self.nickstr[index](self.form[self.attr[index]])
        name = self.attrzh[index]
        return (name, value)

    def get_default_values(self):
        return self.session.user.copy()

    def handle(self, index):
        value = self.inputers[index](self)
        self.form[self.attr[index]] = value
        self.table.set_hover_data(self.get_data_index(index))
                 
    def submit(self):
        if self.readline(buf_size=1, prompt=u'确定修改资料？[Y]es/[N]o ') in ac.ks_yes :
            self.set_user_attr(**self.form)
            self.message(u'修改成功！')
        else:
            self.message(u'取消修改')

    def set_user_attr(self, nickname, realname, address, email, birthday, gender, **kwargs):
        packup = dict(nickname=nickname, realname=realname, address=address,
                      email=email, birthday=birthday, gender=gender)
        manager.userinfo.update_user(self.userid, **packup)
        self.session.user.update(packup)

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

    def initialize(self, user):
        userid = user.get('userid')
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
