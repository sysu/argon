# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng.g import mark
from chaofeng.ui import Form, FinitePagedTable, Password, NullValueError
from chaofeng import ascii as ac
from model import manager
from datetime import datetime
from libframe import BaseAuthedFrame
from view import BaseTextBoxFrame
from edit import handler_edit
from libframe import chunks
from menu import BaseMenuFrame
import config

@mark('user_space')
class UserSpaceFrame(BaseAuthedFrame):

    def initialize(self):
        manager.status.set_status(self.seid,
                                  manager.status.GMENU)
        self.goto('menu', 'user_space')

@mark('user_editdata')
class UserEditDataFrame(BaseAuthedFrame):

    def initialize(self):
        manager.status.set_status(self.seid,
                                  manager.status.EDITUFILE)
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
    MENU = (real, pos, shortcuts, text)
    TITLE = u'编辑个人资料'

    def initialize(self):
        manager.status.set_status(self.seid,
                                  manager.status.EDITUFILE)
        self.setup(self.TITLE, '', self.MENU)

    def goto_next(self, hover):
        self.real = real = self._menu.get_real(hover)
        text = self.user[real]
        self.suspend('edit_text', filename='nickdata',
                     text=text)

    @handler_edit
    def restore(self):
        super(NickDataFrame, self).restore()

    def handler_nickdata(self, text):
        self.cls()
        args = {
            self.real:text,
            }
        try:
            manager.userinfo.update_user(self.userid, **args)
        except None:      ##############  Notice the max buffer len.
            self.write(u'\r\n编辑档案失败！')
        else:
            self.session.user[self.real] = text
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

    shortcuts = {
        ac.k_ctrl_e:"set_sign",
        ac.k_left:"finish",
        }

    def initialize(self):
        manager.status.set_status(self.seid,
                                  manager.status.EDITUFILE)
        self.signs = manager.usersign.get_all_sign(self.userid)
        text =  self.render_str('sign-t', signs=self.signs)
        self.setup(text)

    def set_sign(self):
        text = '\n'.join(self.signs)
        self.suspend('edit_text', filename=u'signature',
                     text=text)

    @handler_edit
    def restore(self):
        self._textbox.restore_screen()

    def handler_signature(self, text):
        if text is None:
            self.write(u'取消设置签名档')
        else:
            text = text.splitlines()
            data = map(lambda x:u'\n'.join(x),
                       chunks(text, 6))
            manager.usersign.set_sign(self.userid, data)
            self.write(u'设置签名档成功！')

    def finish(self, e=None):
        self.goto_back()        

@mark('_query_user_o')
class InnerQueryUserFrame(BaseTextBoxFrame):

    def initialize(self, user):
        manager.status.set_status(self.seid,
                                  manager.status.QUERY)
        text = self.render_str('user-t', **user)
        self.setup(text=text)

    def finish(self, e=None):
        self.goto_back()

@mark('query_user')
class QueryUserFrame(BaseAuthedFrame):

    def initialize(self, userid=None):
        user = manager.query.get_user(self.userid, userid)
        if user :
            self.goto('_query_user_o', user=user)
        else:
            self.pause_back(u'\r\n无此id！')

@mark('query_user_self')
class QueryUserSelfFrame(BaseAuthedFrame):

    def initialize(self):
        self.goto('_query_user_o', user=self.session.user)

@mark('query_user_iter')
class QueryUserIterFrame(QueryUserFrame):

    def initialize(self):
        self.write(ac.clear + u'要查询谁？')
        userid = self.safe_readline(acceptable=ac.isalnum)
        if userid :
            user = manager.query.get_user(self.userid, userid)
            if not user :
                self.pause_back(u'\r\n无此id！')
            self.goto('_query_user_o', user)
        else:
            self.pause_back(u'\r\n取消查询！')

@mark('post_bug')
class PostBugFrame(BaseAuthedFrame):

    def initialize(self):
        manager.status.set_status(self.seid,
                                  manager.status.BUGREPORT)
        self.cls()
        self.render('post_bug_bg')
        title = self.safe_readline(prompt=u'请用几个字简洁地描述bug\r\n')
        if title :
            self.title = title
            self.important = important = self.safe_readline(
                prompt=u'\r\n重要程度（尽量选择低的数字），不输入为 3,\r\n'
                u' 0：安全问题    1：建议性     2：不急着修复\r\n'
                u' 3：一般        4：危险       5：需立即修复\r\n') or '3'
            self.suspend('edit_text', filename='bug', l=12,
                         text=self.render_str('bug-t', title=title,
                                              important=important))
        self.pause_back(u'放弃操作')

    @handler_edit
    def restore(self):
        self.goto_back()

    def handler_bug(self, text):
        self.publish_as_post(text)

    def publish_as_post(self, text):
        pid = manager.action.new_post('BugReport',
                                      self.userid,
                                      u'[bug]/%s\ %s' % (self.important[0],
                                                         self.title),
                                      text,
                                      self.session.ip,
                                      config.BBS_HOST_FULLNAME,
                                      replyable=True)
        manager.post.update_post(pid, mark_g=True)

@mark('test_keyboard')
class TestKeyBoardFrame(BaseAuthedFrame):

    all_test_key = [
        "Cursor Up", "Cursor Down", "Cursor Left", "Cursor Right",
        "Page Up", "Page Down",
        "Home", "End",
        "CTRL+Home", "CTRL+END",
        "CTRL+F2", "CTRL+\\", 
        "backspace", "delete",
        "CTRL+a", "CTRL+z"
        ]

    def initialize(self):
        self.cls()
        self.render('hint/test_keyboard')
        self.title = self.safe_readline(prompt=u'请输入简要的按键方案说明：')
        if not self.title :
            self.pause_back(u'放弃操作')
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
            buf.append(u'    测试 %-15s 的结果为 %r  \r\n' % \
                           (key, self.s(res[key])))
        self.goto('edit_text', filename='keycode', 
                  text=''.join(buf))

    @handler_edit
    def restore(self):
        self.goto_back()

    def handler_keycode(self, text):
        self.publish_as_post(text)
        
    def publish_as_post(self, text):
        manager.action.new_post('Test',
                                self.userid,
                                u'[按键测试] %s ' % self.title,
                                text,
                                self.session.ip,
                                config.BBS_HOST_FULLNAME,
                                replyable=False)

@mark('user_online')
class UserOnlineFrame(BaseAuthedFrame):

    shortcuts = {
        ac.k_left:"goto_back",
        }
    shortcuts_table = {}
    shortcuts_fetch = {
        ac.k_right:"next_frame",
        's':'send_mail',
        }

    _TABEL_START_LINE = 4
    _TABEL_HEIGHT = 20

    def get(self, char):
        if char == ac.k_finish:
            self.fetch_session_do('next_frame')
        self.do_command(self.shortcuts.get(char))
        self.fetch_session_do(self.shortcuts_fetch.get(char))
        self._table.do_command(self.shortcuts_table.get(char))

    def _init_screen(self):
        self.cls()
        self.top_bar()
        self.push('\r\n')
        self.push(config.str['USERONLINE_QUICK_HELP'])
        self.push('\r\n')
        self.push(config.str['USERONLINE_THEAD'])
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

    def fetch_session_do(self, cmd):
        if cmd is None:
            return
        session = self._table.fetch()
        getattr(self, cmd)(session)

    def next_frame(self, session):
        self.suspend('query_user', userid=session['userid'])

    def reload(self):
        self._table.reload()
        self._table.restore_screen()

    def restore(self):
        self._init_screen()

    def initialize(self):
        manager.status.set_status(self.seid,
                                  manager.status.LUSERS)
        self.setup(manager.status.get_session_rank,
                   manager.status.total_online)

    def _wrapper_li(self, li):
        print ('li', li)
        li['nickname'] = manager.userinfo.select_attr(li['userid'],
                                                      'nickname')['nickname']
        return self.render_str('useronline-li', **li)

    def catch_nodata(self):
        raise ValueError(u'It is impossible no body online!')

    def send_mail(self, session):
        self.suspend('send_mail', touserid=session['userid'])
