#!/usr/bin/python2
# -*- coding: utf-8 -*-

__metaclass__ = type

import sys
sys.path.append('../')

from chaofeng.g import mark
from chaofeng.ui import Animation,ColMenu,VisableInput,EastAsiaTextInput,\
    CheckBox, RadioButton, ListBox
import chaofeng.ascii as ac
from libframe import BaseTableFrame, BaseFormFrame, BaseAuthedFrame, list_split
from model import manager
from menu import SelectFrame
import config
import codecs
from libformat import style2telnet
from boardlist import BaseBoardListFrame
import traceback

class BaseEditSystemFileFrame(SelectFrame):

    def initialize(self, filelist):
        filenames = filelist.keys()
        texts = filelist.values()
        super(BaseEditSystemFileFrame, self).initialize(filenames, texts, (3, 5))

    def finish(self):
        filename = self.menu.fetch()
        with codecs.open('static/%s' % filename, encoding="utf8") as f:
            text = f.read().replace('\n', '\r\n')
        self.suspend('edit_text', filename=self.menu.fetch(), text=text,
                     callback=self.save_to_file)

    def save_to_file(self, filename, text):
        text = text.replace('\r\n', '\n')
        with codecs.open('static/%s' % filename, "w", encoding="utf8") as f:
            f.write(text)
        self.message(u'修改系统档案成功！')
        self.pause()
        self.goto_back()

@mark('sys_edit_system_file')
class EditSystemFileFrame(BaseEditSystemFileFrame):

    def initialize(self):
        super(EditSystemFileFrame, self).initialize(config.all_static_file)

@mark('sys_edit_help_file')
class EditHelpFileFrame(BaseEditSystemFileFrame):

    def initialize(self):
        super(EditHelpFileFrame, self).initialize(config.all_help_file)

class BaseEditSectionFormFrame(BaseFormFrame):

    attr = ['sid', 'sectionname', 'description']
    attrzh = [u'讨论区区号', u'分区名称', u'分区描述']

    inputers = [lambda x:x.readline(prompt=u'分区号：', acceptable=ac.isdigit, prefix=x.form.get('sid')),
                lambda x:x.readline(prompt=u'分区名称：', prefix=x.form.get('sectionname')),
                lambda x:x.readline(prompt=u'分区描述：', prefix=x.form.get('description'))]

    def get_default_values(self):
        return self.section
        
    def get_data_index(self, index):
        return (self.attrzh[index], self.form.get(self.attr[index]))

    def handle(self, index):
        self.form[self.attr[index]] = self.inputers[index](self)
        self.table.set_hover_data(self.get_data_index(index))

    def get_data_len(self):
        return len(self.attr)

    def handle_submit(self):
        raise NotImplementedError
    
    def submit(self):
        if self.readline(prompt=u'确认？',buf_size=5) in ac.ks_yes :
            self.handle_submit()
            self.message(u'操作成功！')
            self.pause()
            self.goto_back()
        else:
            self.message(u'取消操作')
        self.pause()

@mark('sys_new_section')
class NewSectionFormFrame(BaseEditSectionFormFrame):

    def handle_submit(self):
        manager.admin.add_section(self.userid, sid=self.form['sid'],
                                  sectionname=self.form['sectionname'],
                                  description=self.form['description'])

    def initialize(self, section=None):
        if section is None:
            section = {}
        self.section = section
        super(BaseEditSectionFormFrame, self).initialize()

@mark('sys_edit_section')
class UpdateSectionFormFrame(BaseEditSectionFormFrame):

    def handle_submit(self):
        manager.admin.update_section(self.userid,
                                     sid=self.section['sid'], 
                                     sectionname=self.form['sectionname'],
                                     description=self.form['description'])
        
    def end(self, s):
        self.writeln(s)
        self.pause()
        self.goto_back()

    def initialize(self, section=None):
        if section is None:
            sid = self.readline_safe(prompt=u'请输入讨论区编号：', acceptable=ac.isdigit)
            if sid.isdigit() :
                section = manager.query.get_section(sid)
                if not section :
                    self.end(u'没有该分区！')
            else:
                self.end(u'非法输入！')
        self.section = section
        super(UpdateSectionFormFrame, self).initialize()                    

class BaseEditBoardFormFrame(BaseFormFrame):

    attr = ['boardname', 'description', 'sid', 'is_open', 'is_openw']
    attrzh = [u'讨论区名称',u'讨论区描述',u'所属讨论区分区',u'公开',u'允许回复']

    inputers = [lambda x:x.readline(prompt=u'输入新讨论区名称： ', acceptable=ac.isalpha,
                                    prefix=x.form['boardname']),
                lambda x:x.readline(prompt=u'讨论区描述： ', prefix=x.form['description']),
                lambda x:x.read_sid(),
                lambda x:x.read_true_or_false(x.form['is_open'],
                                              [u'设置为不公开？',u'设置为公开？']),
                lambda x:x.read_true_or_false(x.form['is_openw'],
                                              [ u'设置为不可回复？', u'设置为允许回复？'])
                ]

    def read_true_or_false(self, value, prompt):
        p = prompt[0] if value else prompt[1]
        if self.readline(buf_size=3, prompt=p) :
            return not value
        else:
            return value

    def read_sid(self):
        self.cls()
        radio = self.load(RadioButton, self.sections_op, default=self.form['sid'])
        res = radio.read()
        self.restore()
        return res
        
    def get_default_values(self):
        openr, openw = manager.admin.is_open_board(self.userid,
                                                   self.board.get('boardname'))
        print ('pp', openr, openw)
        sid = self.board.get('sid')
        return dict( boardname=self.board.get('boardname') or '',
                     description=self.board.get('description') or '',
                     sid=self.board.get('sid'),
                     is_open=openr, is_openw=openw)

    def get_data_index(self, index):
        if index == 2:
            sid = self.form[self.attr[index]]
            if sid is None:
                return (self.attrzh[index], '')
            else:
                return (self.attrzh[index], self.sectionstr[sid])
        else:
            return (self.attrzh[index], self.form[self.attr[index]])

    def handle(self, index):
        self.form[self.attr[index]] = self.inputers[index](self)
        self.table.set_hover_data(self.get_data_index(index))

    def get_data_len(self):
        return len(self.attr)

    def check_boardattr(self):
        if len(self.form['boardname']) < 3 :
            self.message(u'讨论区名过短')
        elif len(self.form['description']) < 3:
            self.message(u'讨论区描述过短')
        elif self.form['sid'] == None:
            self.message(u'没有正确设置讨论区分区')
        else : return True
        return False

    def submit(self):
        if self.check_boardattr() :
            if self.readline(prompt=u'确认修改？',buf_size=5) in ac.ks_yes :
                self.handle_submit()
                self.pause()
                self.goto_back()
            else:
                self.message(u'取消操作')
        self.pause()
    
    def initialize(self, board=None):
        sections = manager.query.get_all_section_with_rownum()
        self.sectionstr = map(lambda x: u'%s区 %s' % (x.rownum, x.sectionname) , sections)
        self.sections_op = self.sectionstr
        print self.sections_op
        if board is None:
            board = {}
        self.board = board
        super(BaseEditBoardFormFrame, self).initialize()

    def handle_submit(self):
        raise NotImplementedError

@mark('sys_new_board')
class AddBoardFrame(BaseEditBoardFormFrame):

    def handle_submit(self):
        manager.admin.add_board(self.userid,
                                boardname=self.form['boardname'],
                                description=self.form['description'],
                                sid=self.form['sid'], is_open=self.form['is_open'],
                                is_openw=self.form['is_openw'])
        self.message(u'操作成功！')

@mark('sys_set_boardattr')
class UpdateBoardFrame(BaseEditBoardFormFrame):

    '''
    Update board attr.
    '''

    def handle_submit(self):
        manager.admin.update_board(self.userid,
                                   boardname=self.form['boardname'], bid=self.board['bid'],
                                   description=self.form['description'],
                                   sid=self.form['sid'], is_open=self.form['is_open'],
                                   is_openw=self.form['is_openw'])
        self.message(u'操作成功！')


    def initialize(self, board=None):
        '''
        board is dict then should holds bid, boardname, description, sid,
        is_openw key, and update by bid.
        '''
        if board is None:
            board = self.get_board_iter()
        super(UpdateBoardFrame, self).initialize(board)

    def get_board_iter(self):
        boardname = self.readline_safe(prompt=u'请输入讨论区名字：')
        board = manager.query.get_board(self.userid,  boardname)
        print board
        if not board :
            self.write(u'没有该讨论区！')
            self.pause()
            self.goto_back()
        return board

@mark('sys_add_bm')
class AddBoardManager(BaseAuthedFrame):

    def initialize(self):
        self.cls()
        try:
            userid = self.readline(prompt=u'请输入欲任命的使用者帐号：')
            self.writeln('\r\n')
            user = manager.query.get_user(self.userid, userid)
            if not user :
                raise ValueError(u'没有该用户！')
            userid = user['userid']
            self.writeln(u'  任命 %s ' % userid)
            boardname = self.readline(prompt=u'请输入该使用者将管理的讨论区名称：')
            self.writeln('\r\n')
            board = manager.query.get_board(self.userid, boardname)
            if not board :
                raise ValueError(u'没有该讨论区!')
            boardname = board['boardname']
            if self.readline(prompt=u'\r\n任命 %s 为 %s 的版主，确定？[Y/N]' % (userid, boardname),
                             buf_size=1) :
                manager.admin.join_bm(self.userid, userid, boardname)
                self.writeln('\r\n')
                self.writeln(u'设置成功！')
            else:
                raise ValueError(u'取消操作！')
        except ValueError as e:
            self.writeln(u'\r\n操作失败 %s' % e.message)
        self.pause()
        self.goto_back()

@mark('sys_remove_bm')
class RemoveBoardManager(BaseAuthedFrame):

    def initialize(self):
        self.cls()
        try:
            userid = self.readline(prompt=u'请输入欲离职的使用者帐号：')
            self.writeln('\r\n')
            user = manager.query.get_user(self.userid, userid)
            if not user :
                raise ValueError(u'没有该用户！')
            userid = user['userid']
            self.writeln(u'  %s 要离职 ' % userid)
            boardname = self.readline(prompt=u'请输入要辞去的版名：')
            self.writeln('\r\n')
            board = manager.query.get_board(self.userid, boardname)
            if not board :
                raise ValueError(u'没有该讨论区!')
            boardname = board['boardname']
            if self.readline(prompt=u'\r\n%s 从 %s 离职，确定？[Y/N]' % (userid, boardname),
                             buf_size=1) :
                self.writeln('\r\n')
                manager.admin.remove_bm(self.userid, userid, boardname)
                self.writeln(u'设置成功！')
            else:
                raise ValueError(u'取消操作！')
        except ValueError as e:
            self.writeln(u'\r\n操作失败 %s' % e.message)
        self.pause()
        self.goto_back()

@mark('sys_edit_team')
class EditTeamFrame(BaseAuthedFrame):

    def _initialize(self):
        self.listbox = self.load(ListBox, start_line=4, height=15)
        self.cls()
        self.write(''.join([self.render_str('top'),
                            '\r\n',
                            config.str['EDIT_LIST_QUICK_HELP'],
                            '\r\n',
                            u'[0;1;44m    帐号                     帐号                    '
                            u'帐号                      [m',
                            self.render_str('bottom')]))
        self.refresh_items()

    def initialize(self, teamname):
        self.teamname = teamname
        self._initialize()
        
    def refresh_items(self):
        self.userids = list(manager.team.all_menber(self.teamname))
        self.listbox.update(self.userids, self.userids)

    def add(self):
        userids = self.readline(prompt=u'输入要增加的id：').split(',')
        succ = 0
        failed = 0
        for userid0 in userids :
            user = manager.userinfo.get_user(userid0)
            if user :
                manager.team.join_team(user['userid'], self.teamname)
                succ += 1
            else:
                failed += 1
        self.message(u'成功加入 %s , 不存在的帐号 ：%s' % (succ, failed))
        self.refresh_items()

    def remove(self):
        if self.userids :
            manager.team.remove_team(self.listbox.fetch(), self.teamname)
            self.message(u'成功移除')

    def get(self, char):
        if self.userids :
            if char in config.hotkeys['edit_list_ui'] :
                getattr(self.listbox, config.hotkeys['edit_list_ui'][char])()
        if char in config.hotkeys['edit_list']:
            getattr(self, config.hotkeys['edit_list'][char])()

    def readline(self, prompt, acceptable=ac.is_safe_char, finish=ac.ks_finish,
                  buf_size=20, prefix=u''):
        prompt = ''.join([ac.move2(24,1), ac.kill_line, prompt])
        res = super(EditTeamFrame, self).readline(prompt=prompt, acceptable=acceptable,
                                                      finish=finish, buf_size=buf_size,
                                                      prefix=prefix)
        self.render('bottom')
        if hasattr(self, 'listbox'):
            self.listbox.fix_cursor()
        return res

    def message(self, msg):
        self.write(''.join([ac.move2(23,2), ac.kill_line, msg]))
        self.listbox.fix_cursor()

@mark('sys_edit_team_iter')
class EditTeamIterFrame(EditTeamFrame):

    def initialize(self):
        self.cls()
        self.teamname = self.readline(prompt=u'请输入欲管理的组名: ')
        if not manager.team.exists(self.teamname):
            self.write(u'没有该组！')
            self.pause()
            self.goto_back()
        self._initialize()

@mark('sys_edit_user_team')
class EditUserTeamFrame(BaseAuthedFrame):
    
    def _initialize(self):
        self.listbox = self.load(ListBox, start_line=4, height=15)
        self.cls()
        self.write(''.join([self.render_str('top'),
                            '\r\n',
                            config.str['EDIT_LIST_QUICK_HELP'],
                            '\r\n',
                            u'[0;1;44m    组号                     组号                    '
                            u'组号                      [m',
                            self.render_str('bottom')]))
        self.refresh_items()

    def initialize(self, userid):
        self.euserid = userid
        self._initialize()
        
    def refresh_items(self):
        self.teams = list(manager.team.user_teams(self.euserid))
        self.texts = map(lambda x : '%s(%s)' % tuple(x), zip(self.teams,
                                                             manager.team.get_names(self.teams)))
        self.listbox.update(self.texts, self.teams)

    def add(self):
        teamnames = self.readline(prompt=u'输入要增加的组名：').split(',')
        succ = 0
        failed = 0
        for teamname in teamnames :
            if manager.team.exists(teamname) :
                manager.team.join_team(self.euserid, teamname)
                succ += 1
            else:
                failed += 1
        self.message(u'成功加入 %s , 不存在的组 ：%s' % (succ, failed))
        self.refresh_items()

    def remove(self):
        if self.teams:
            manager.team.remove_team(self.euserid, self.listbox.fetch())
            self.message(u'成功移除')

    def get(self, char):
        if self.teams :
            if char in config.hotkeys['edit_list_ui'] :
                getattr(self.listbox, config.hotkeys['edit_list_ui'][char])()
        if char in config.hotkeys['edit_list']:
            getattr(self, config.hotkeys['edit_list'][char])()

    def readline(self, prompt, acceptable=ac.is_safe_char, finish=ac.ks_finish,
                  buf_size=20, prefix=u''):
        prompt = ''.join([ac.move2(24,1), ac.kill_line, prompt])
        res = super(EditUserTeamFrame, self).readline(prompt=prompt, acceptable=acceptable,
                                                      finish=finish, buf_size=buf_size,
                                                      prefix=prefix)
        self.render('bottom')
        if hasattr(self, 'listbox'):
            self.listbox.fix_cursor()
        return res

    def message(self, msg):
        self.write(''.join([ac.move2(23,2), ac.kill_line, msg]))
        self.listbox.fix_cursor()
    
@mark('sys_edit_user_team_iter')
class EditUserTeamIterFrame(EditUserTeamFrame):

    def initialize(self):
        self.cls()
        euserid = self.readline(prompt=u'请输入欲设置的用户名: ')
        user = manager.userinfo.get_user(euserid)
        if not user:
            self.write(u'没有该组！')
            self.pause()
            self.goto_back()
        self.euserid = user['userid']
        self._initialize()

@mark('edit_default_favourite')
class SetDefaultFavouriteFrame(BaseBoardListFrame):

    def catch_nodata(self, e):
        self.cls()
        self.writeln(u'没有任何版块！')
        self.pause()
        self.goto_back()

    def get_default_index(self):
        return 0

    def get_data(self, start, limit):
        return self.boards[start:start+limit]

    def finish(self):
        pass

    def add_to_fav(self):
        manager.favourte.add_default(self.table.fetch()[u'bid'])
        self.message(u'成功加入默认用户的收藏夹！')

    def remove_fav(self):
        manager.favourte.remove_default(self.table.fetch()[u'bid'])
        self.message(u'成功移除默认用户的收藏夹！')

    def suspend(self):
        pass

    def initialize(self):
        self.boards = manager.query.get_boards(self.userid, None)
        self.board_total = len(self.boards)
        super(SetDefaultFavouriteFrame, self).initialize()

@mark('super')
class SuperSystemFrame(BaseAuthedFrame):

    def initialize(self):
        self.cls()
        self.render('super')
        self.loop()

    def loop(self):
        while True:
            cmd = filter(lambda x:x, self.readline(prompt='argo$ ', buf_size=70).split())
            self.write('\r\n')
            if not cmd : continue
            action = 'action_%s' % cmd[0]
            if action == 'action_bye':
                self.goto_back()
            if hasattr(self, action) :
                try:
                    getattr(self, action)(*cmd[1:])
                except Exception as e:
                    traceback.print_exc()
                    self.writeln('[ERROR] %s' % e.message)

    def action_help(self, cmd='help'):
        u'''
        查询帮助：    help cmd
        cmd包括：
            rt                                      // register_team
            dt                                      // drop_team
            qt                                      // query_all_team
        '''
        action = 'action_%s' % cmd
        if hasattr(self, action):
            self.writeln(getattr(self, action).__doc__.replace('\n', '\r\n'))
        else:
            raise ValueError(u'没有此命令！')

    def action_rt(self, teamid, teamname):
        u'''
        添加一个组:    rt teamid teamname
        其中teamid应该为全部大写字母。
        '''
        if manager.team.exists(teamid):
            raise ValueError(u'此组名已经被使用！')
        if not teamid.isalpha():
            raise ValueError(u'组名应该全部为大写字符！')
        teamid = teamid.upper()
        manager.team.register_team(teamid, teamname)
        self.writeln(u'[SUCC] 注册组 %s 成功！' % teamid)

    def action_dt(self, teamid, force=False):
        u'''
        删除一个组：    dt teamid force=False
        删除一个组
        eg:
            drop_team TEST // 检查TEST是否存在
            drop_team TEST dfa // 检查TEST是否存在
        '''
        if not force :
            if not manager.team.exists(teamid):
                raise ValueError(u'没有该组！')
        manager.team.drop_team(teamid)
        self.writeln('[SUCC] 移除组 %S 成功！' % teamid)
        
    def action_qt(self, split=4):
        u'''
        输出当前全部的组：    qt split=4
        split表示一行多少个。
        '''
        split = int(split)
        teams = manager.team.all_team()
        for d in list_split(teams, split) :
            self.writeln(' '.join(d))
            self.pause()
