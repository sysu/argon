# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import Frame,EndInterrupt,Timeout
from chaofeng.g import mark,is_chchar
from chaofeng.ui import EastAsiaTextInput,Password,DatePicker,Form,ColMenu
from chaofeng import ascii as ac
from model import manager
from datetime import datetime
from argo_frame import ArgoFrame
from menu import MenuFrame
from view import ArgoTextBoxFrame
from MySQLdb import DataError
import config

@mark('user_space')
class UserSpaceFrame(MenuFrame):

    def initialize(self):
        super(UserSpaceFrame,self).initialize()
        menu_data = self.get_tidy_data()
        background = self.render_str('menu_user_space')
        anim_data = self.get_anim_data()
        self.setup(menu_data, 1, 11, background, 0, anim_data)

    def show_help(self):
        self.suspend('help',page='user_space')

    def get_tidy_data(self):
        return ColMenu.tidy_data(config.menu['user_space'])

    def finish(self):
        self.suspend(self.menu.fetch())

    def do_help(self):
        self.write(ac.move2(11,0)+static['help_user_space'])
        self.pause()
        self.do_refresh()

@mark('user_editdata')
class UserEditDataFrame(ArgoFrame):

    pos = ((4,24),
           (5,24),
           (6,24),
           (7,24),
           (8,24),
           (9,24))
            
    def initialize(self):
        self.cls()
        self.render('edit_user_data')
        acc = self.session.user.copy()
        self.zh_input = self.load(zhTextInput)
        self.date_picker = self.load(DatePicker)
        self.f = self.load(Form)
        self.f.run((self.read_nickname,
                    self.read_realname,
                    self.read_address,
                    self.read_email,
                    self.read_birthday,
                    self.read_gender),
                   self.pos,
                   acc=acc)
        self.write(u'\r\n\r\n确认修改您的资料？y/else.')
        d = self.readline()
        if d == 'y' :
            manager.userinfo.update_user(**acc)
            self.write(u'\r\n修改成功!')
        else:
            self.write(u'\r\n取消编辑')
        self.pause()
        self.goto_back()

    def read_nickname(self, acc):
        res = self.zh_input.read(buf=list(acc['nickname']),stop=ac.k_ctrl_c)
        if res is False:
            return False
        acc['nickname'] = res
        return True

    def read_realname(self, acc):
        realname = acc.get('realname') or ''
        res = self.zh_input.read(buf=list(realname),stop=ac.k_ctrl_c)
        if res is False:
            return False
        acc['realname'] = res 
        return True

    def read_address(self, acc):
        address = acc.get('address') or ''
        res = self.zh_input.read(buf=list(address),stop=ac.k_ctrl_c)
        if res is False:
            return False
        acc['address'] = res 
        return True

    def read_email(self, acc): 
        email = acc.get('email') or ''
        res = self.zh_input.read(buf=list(email),stop=ac.k_ctrl_c)
        if res is False:
            return False
        acc['email'] = res or None
        return True

    def read_birthday(self, acc):
        res = self.date_picker.read(buf=list(acc['birthday'].strftime("%Y%m%d")),
                                    stop=ac.k_ctrl_c)
        if res is False:
            return False
        acc['birthday'] = res
        return True

    def read_gender(self, acc):
        res = self.zh_input.read(buf=list('M' if acc['gender'] else 'F'),stop=ac.k_ctrl_c)
        if res is False:
            return False
        if res in 'FM-':
            acc['gender'] = 0 if res=='F' else ( 1 if res=='M' else 2)
            return True

@mark('user_nickdata')
class NickDataFrame(ArgoFrame):

    options = ('shai','contact','want','job','marriage','about')
    def initialize(self):
        self.cls()
        self.render('nickdata')
        res = self.select(lambda o : self.write(ac.move2(12,1)+ ac.clear1+
                                                unicode(self.session.user[o])+
                                                ac.move2(10,6) + ac.kill_to_end +
                                                config.options['nickdata'][o]),
                          self.options)
        if res is not False:
            self.sel = self.options[res]
            self.suspend('edit_text', filename=config.options['nickdata'][self.sel])
        else:
            self.write(u'\r\n取消设置！')
            self.pause()
            self.goto_back()

    def restore(self):
        self.cls()
        args = {
            self.sel:self.pipe,
            }
        if args[self.sel] is None:
            self.write(u'\r\n取消设置资料')
        else:
            try:
                manager.userinfo.update_user(self.userid,
                                             **args)
            except:
                self.write(u'\r\n编辑档案失败！')
            else:
                self.session.user[self.sel] = self.pipe
                self.write(u'\r\n编辑档案成功！')
        self.pause()
        self.goto_back()

@mark('user_change_passwd')
class ChangePasswdFrame(ArgoFrame):

    def initialize(self):
        self.write(ac.clear + u'开始修改密码...\r\nCtrl+C退出取消本次活动。')
        self.write(u'\r\n\r\n请输入旧密码进行确认 ：')
        ui_passwd = self.load(Password)
        ui_passwd.reset()

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
class EditSignFrame(ArgoFrame):

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
        self.suspend('edit_text', filename=u'签名档',text=text, l=r*6, split=True)

    def restore(self):
        self.cls()
        if self.pipe is None:
            self.write(u'取消设置签名档')
            self.goto_back()
        data = map(lambda x:'\r\n'.join(x),
                   chunks(self.pipe,6))
        manager.usersign.set_sign(self.userid, data)
        self.write(u'设置签名档成功！')
        self.pause()
        self.goto_back()

@mark('query_user')
class QueryUserFrame(ArgoTextBoxFrame):

    def initialize(self, userid):
        super(QueryUserFrame,self).initialize()
        self.setup()
        self.cls()
        self.set_text(self.query_user_normal(userid))

    def query_user_normal(self, userid):
        user = manager.userinfo.get_user(userid)
        if user is None :
            self.write(u'没有该用户！')
            self.pause()
            self.goto_back()
        else:
            return self.render_str('user-t',**user)

    def finish(self,a):
        self.goto_back()

@mark('query_user_self')
class QueryUserSelfFrame(QueryUserFrame):

    def initialize(self):
        super(QueryUserSelfFrame,self).initialize(self.userid)

@mark('query_user_iter')
class QueryUserIterFrame(QueryUserFrame):

    def initialize(self):
        self.write(ac.clear + u'要查询谁？')
        userid = self.readline(acceptable=ac.is_alnum)
        print repr(userid)
        super(QueryUserIterFrame,self).initialize(userid)

