# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import Frame,static,EndInterrupt,Timeout,BindFrame
from chaofeng.g import mark,is_chchar
from chaofeng.ui import TextInput,Password,DatePicker
from chaofeng import ascii as ac
from libtelnet import str_top,str_bottom
from model import *
from datetime import datetime
from base_menu import BaseMenuFrame
from argo_frame import ArgoBaseFrame
import config

class UsernameInput(TextInput):

    def acceptable(self,c):
        try:
            return c.isalnum() or is_chchar(c.decode('gbk')) or c == '+'
        except:
            return False

@mark('register')
class RegisterFrame(ArgoBaseFrame):

    background = ac.clear + static['page/register_notice']
    ban_userid = ['guest','new']
    ix_name = TextInput(prompt= u'请输入帐号名称 (Enter User ID, leave blank to abort): ')
    ix_passwd = Password(prompt= u'请设定您的密码 (Setup Password): ')
    timeout = 150

    def check_userid(self,userid):
        if userid in self.ban_userid :
            self.write(u'抱歉, 您不能使用该id。 请再拟。\r\n')
        elif len(userid) < 3 :
            self.write(u'抱歉，您的id太短撩。 请再拟。\r\n')
        elif db_orm.check_user_not_exist(userid) != True :
            self.write(u'抱歉，您的id已经被注册了。 请再拟。\r\n')
        else : return True
        return False

    def check_passwd(self,passwd):
        if len(passwd) < 6 :
            self.write(u'密码太短了，请大于6位。\r\n')
            return False
        return True

    def register(self,userid,passwd):
        print userid
        print passwd
        db_orm.add_user(userid,passwd,{
                'firstlogin':datetime.now(),
                'firsthost':self.session.ip,
                })
        self.write(ac.clear+static['page/register_succ'] % userid)
        self.pause()
        self.goto('welcome')
    
    def initialize(self):
        self.render_background()
        i_name = self.load(self.ix_name)
        i_passwd = self.load(self.ix_passwd)
        with Timeout(self.timeout,EndInterrupt) :
            while True :
                userid = i_name.readln()
                if self.check_userid(userid) : break
            while True :
                passwd = i_passwd.readln()
                if self.check_passwd(passwd) : break
        self.register(userid,passwd)

    def get(self,data):
        if data == ac.k_ctrl_c :
            self.write(u'\r\n你按下了Ctrl+C ，将会取消本次的活动。\r\n :-) 别害怕，你可以再来一次。')
            self.pause()
            self.goto('welcome')

@mark('user_space')
class UserSpaceFrame(BaseMenuFrame):

    shortcuts = config.default_shortcuts

    def initialize(self):
        super(UserSpaceFrame,self).initialize(
            static['menu_userspace'],
            config.menu['userspace'])

    def do_help(self):
        self.write(ac.move2(11,0)+static['help_user_space'])
        self.pause()
        self.do_refresh()

@mark('user_edit_data')
class UserEditDataFrame(Frame):

    @staticmethod
    def check_nickname(data):
        return True
    
    @staticmethod
    def check_realname(data):
        return True
    
    @staticmethod
    def check_address(data):
        return True

    @staticmethod
    def check_email(data):
        return True

    @staticmethod
    def check_gender(data):
        return data == 'F' or data == 'M'

    def initialize(self):
        self.write(ac.clear+str_top(self))
        u = self.session['_user'].dump_attr()
        u['gender'] = u'女' if u['gender'] else u'男'
        try:
            self.write(static['user_edit_data'] % u)
        except TypeError:
            self.write(u'数据还没填写！下面开始填写你的数据咯~\r\n')
        else:
            self.write(u'Ctrl+c返回，任意键开始修改。')
            self.pause()
        u = self.session['_user'].dump_attr()
        self.write(u'\r\n\r\n请逐项修改,直接按 <ENTER> 代表使用 [] 内的资料。\r\n')

        input_text = self.sub(TextInput)
        for key,des in ( ('nickname',u'\r\n昵称 [%s] :'%u['nickname']),
                         ('realname',u'\r\n真实姓名 [%s] :'%u['realname']),
                         ('address',u'\r\n居住地址 [%s] :'%u['address']),
                         ('email',u'\r\n电子信箱 [%s] :'%u['email']),
                         ('gender',u'\r\n性别 M.男 F.女 [%s]:' % 'F' if u['gender'] else 'M')) :
            self.write(des)
            input_text.clear()
            text = input_text.read_until()
            if len(text) and getattr(self,'check_'+key)(text) :
                u[key] = text

        u['gender'] = 1 if u['gender'] == 'F' else 0

        self.write(u'\r\n生日 [%s] : ' % u['birthday'].isoformat())
        birthday = self.sub(DatePicker).read_until()
        if birthday :
            u['birthday'] = birthday

        self.write(u'\r\n确定要改变吗 (yes/NO)? [N]')
        g = self.read()
        if g == 'y' :
            self.session['_user'].update_dict(u)
            self.session['_user'].update_user(['nickname','realname','address','email','birthday','gender'])
            self.write(u'\r\修改成功！')
        self.goto(mark['user_edit_data'])

    def get(self,data):
        if data == ac.k_ctrl_c :
            self.goto(mark['user_space'])

@mark('change_passwd')
class ChangePasswdFrame(Frame):

    def initialize(self):
        self.write(ac.clear + u'开始修改密码...\r\nCtrl+C退出取消本次活动。')
        self.write(u'\r\n\r\n请输入旧密码进行确认 ：')
        ui_passwd = self.sub(Password)
        passwd = ui_passwd.read_until()
        if not self.session['_user'].check_passwd(passwd):
            self.write(u'\r\n很抱歉, 您输入的密码不正确。')
            self.pause()
            self.goto(mark['user_space'])
        self.write(u'\r\n请设定新密码：')
        ui_passwd.clear()
        pass1 = ui_passwd.read_until()
        self.write(u'\r\n请重新输入新密码以确认:')
        ui_passwd.clear()
        passwd = ui_passwd.read_until()
        if pass1 != passwd :
            self.write(u'新密码确认失败, 无法设定新密码。')
            self.pause()
            self.goto(mark['user_space'])
        self.session['_user'].update_dict({"passwd":passwd})
        self.session['_user'].set_passwd(passwd)
        self.write(u'\r\n\r\n密码修改成功！')
        self.pause()
        self.goto(mark['user_space'])

    def get(self,data):
        if data == ac.k_ctrl_c :
            self.goto(mark['user_space'])
