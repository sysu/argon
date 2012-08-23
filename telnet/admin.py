#!/usr/bin/python2
# -*- coding: utf-8 -*-

__metaclass__ = type

import sys
sys.path.append('../')

import codecs
import datetime
from model import manager
from libframe import BaseEditFrame, BaseAuthedFrame, BaseBoardListFrame,\
    list_split
from chaofeng.g import mark
from chaofeng.ui import Form, ListBox, PagedTable, NullValueError, TableLoadNoDataError
import config
import chaofeng.ascii as ac
import traceback

@mark('sys_edit_system_file')
class EditSystemFileFrame(BaseEditFrame):

    def initialize(self, filename):
        self.filename = filename
        with codecs.open('static/%s' % filename, encoding="utf8") as f:
            text = f.read().replace('\n', '\r\n')
        super(EditSystemFileFrame, self).initialize(text=text)

    def finish(self):
        text = self.e.fetch_all().replace('\r\n', '\n')
        with codecs.open('static/%s' % self.filename, "w", encoding="utf8") as f:
            f.write(text)
        self.message(u'修改系统档案成功！')
        self.pause()
        self.goto_back()

@mark('sys_new_section')
class NewSectionsFrame(BaseAuthedFrame):

    def initialize(self):
        self.cls()
        self.render('top')
        text = self.render_str('hint/new_section').split('\r\n----\r\n')
        self.form = self.load(Form, [
                ('sid', text[0], self.handler_sid),
                ('sectionname', text[1], self.handler_sectionname),
                ('description', text[2], self.handler_description),
                ('introduction', text[3], self.handler_introduction),
                ])
        data = self.form.read()
        if not data :
            self.writeln(u'取消操作！')
            self.pause()
            self.goto_back()
        self.cls()
        self.render('sys_section_preview', **data)
        confirm = self.readline(prompt=u'输入资料完成，确定新建分区？YES确定 >>')
        if confirm == 'YES' :
            manager.section.add_section(sid=data['sid'],
                                        sectionname=data['sectionname'],
                                        description=data['description'],
                                        introduction=data['introduction'])
            self.writeln(u'\r\n增加分区成功！')
        else:
            self.writeln(u'\r\n取消操作！')
        self.pause()
        self.goto_back()

    def handler_sid(self, sid):
        if not sid.isdigit() :
            raise ValueError(u'分区号应该是一个数字')
        g = int(sid)
        if manager.section.get_section_by_sid(g) :
            raise  ValueError(u'该分区号已经被使用！')
        return g

    def handler_sectionname(self, sectionname):
        if len(sectionname) >= 20 :
            raise ValueError(u'分区名太长！')
        return sectionname

    def handler_description(self, description):
        if len(description) >= 50 :
            raise ValueError(u'分区的中文描述太长！')
        return description

    def handler_introduction(self, introduction):
        if len(introduction) >= 140 :
            raise ValueError(u'分区的介绍太长！')
        return introduction

@mark('sys_edit_section')
class EditSectionFrame(BaseAuthedFrame):

    def handler_sid(self, sid):
        if not sid:
            raise ValueError(u'\r\n取消操作！')
        if not sid.isdigit():
            raise ValueError(u'\r\n分区号是一个数字！')
        section = manager.section.get_section_by_sid(sid)
        if section :
            return int(sid), section
        else:
            raise ValueError(u'\r\n没有该讨论区！')        

    def initialize(self):
        sid = self.readline(prompt=u'请输入欲修改的讨论区号：')
        try:
            self.sid, default = self.handler_sid(sid)
        except ValueError as e:
            self.writeln(e.message)
            self.pause()
            self.goto_back()
        self.cls()
        self.render('top')
        text = self.render_str('hint/edit_section').split('\r\n----\r\n')
        self.form = self.load(Form, [
                ('sectionname', text[0], self.handler_sectionname),
                ('description', text[1], self.handler_description),
                ('introduction', text[2], self.handler_introduction),
                ])
        default['sid'] = unicode(default['sid'])
        self.form.read(default=default)
        self.writeln(u'\r\n全部设置完毕！')
        self.pause()
        self.goto_back()

    def handler_sectionname(self, sectionname):
        if not sectionname:
            return
        if len(sectionname) >= 20 :
            raise ValueError(u'分区名太长！')
        manager.section.update_section(self.sid, sectionname=sectionname)

    def handler_description(self, description):
        if not description:
            return
        if len(description) >= 50 :
            raise ValueError(u'分区的中文描述太长！')
        manager.section.update_section(self.sid, description=description)

    def handler_introduction(self, introduction):
        if not introduction:
            return
        if len(introduction) >= 140 :
            raise ValueError(u'分区的介绍太长！')
        manager.section.update_section(self.sid, introduction=introduction)
        
@mark('sys_new_board')
class NewBoardFrame(BaseAuthedFrame):

    def initialize(self):
        self.cls()
        self.render('top')
        text = self.render_str('hint/new_board').split('\r\n----\r\n')
        self.form = self.load(Form, [
                ('boardname', text[0], self.handler_boardname),
                ('description', text[1], self.handler_description),
                ('sid', text[2], self.handler_sid),
                ('allowteam', text[3], self.handler_allowteam),
                ('postteam', text[4], self.handler_postteam),
                ('denyteam', text[5], self.handler_denyteam),
                ('adminteam', text[6], self.handler_adminteam),
                ])
        data = self.form.read()
        if not data :
            self.writeln(u'取消操作！')
            self.pause()
            self.goto_back()
        self.cls()
        self.render('sys_board_preview', **data)
        confirm = self.readline(prompt=u'输入资料完成，确认新建版块？YES确认')
        if confirm == 'YES' :
            manager.admin.add_board(self.userid, **data)
            self.writeln(u'\r\n增加版块成功！')
        else:
            self.writeln(u'\r\n\取消操作!')
        self.pause()
        self.goto_back()
            
    def handler_boardname(self, boardname):
        if len(boardname) >= 20 :
            raise ValueError(u'版块名太长！')
        if manager.board.get_board(boardname):
            raise ValueError(u'该版块名已被使用！')
        return boardname

    def handler_description(self, description):
        if len(description) >= 49 :
            raise ValueError(u'版块描述太长！')
        return description

    def handler_sid(self, sid):
        if not sid.isdigit() :
            raise ValueError(u'分区应该是一个数字！')
        return int(sid)

    def handler_allowteam(self, allteam):
        return allteam or 'SYS_GUEST,SYS_WELCOME,SYS_USER'

    def handler_postteam(self, postteam):
        return postteam or 'SYS_USER'

    def handler_denyteam(self, denyteam):
        return denyteam or 'SYS_DENY_GLOBAL,SYS_{}_DENY'

    def handler_adminteam(self, adminteam):
        return adminteam or 'SYS_SYSOPS,SYS_{}_BM'

@mark('sys_set_boardattr')
class EditBoardAttrFrame(BaseAuthedFrame):

    def initialize(self, boardname):
        board = manager.board.get_board(boardname)
        if not board:
            self.writeln(u'没有该版块！')
            self.pause()
            self.goto_back()
        self.cls()
        self.render('top')
        text = self.render_str('hint/edit_board').split('\r\n----\r\n')
        self.form = self.load(Form, [
                ('description', text[0], self.handler_description),
                ('sid', text[1], self.handler_sid),
                ('allowteam', text[2], self.handler_allowteam),
                ('postteam', text[3], self.handler_postteam),
                ('denyteam', text[4], self.handler_denyteam),
                ('adminteam', text[5], self.handler_adminteam),
                ])
        self.bid = board['bid']
        self.boardname = boardname = board['boardname']
        board['sid'] = unicode(board['sid'])
        board['allowteam'] = ','.join(manager.userperm.get_board_allow(boardname))
        board['postteam'] = ','.join(manager.userperm.get_board_post(boardname))
        board['denyteam'] = ','.join(manager.userperm.get_board_deny(boardname))
        board['adminteam'] = ','.join(manager.userperm.get_board_admin(boardname))
        self.form.read(default=board)
        self.writeln(u'全部设置完毕！')
        self.pause()
        self.goto_back()

    def handler_description(self, description):
        if description == '':
            return
        if len(description) >= 49 :
            raise ValueError(u'版块描述太长！')
        manager.board.update_board(self.bid, description=description)

    def handler_sid(self, sid):
        if sid == '':
            return
        if not sid.isdigit() :
            raise ValueError(u'分区应该是一个数字！')
        manager.board.update_board(self.bid, sid=sid)
        
    def handler_allowteam(self, teams):
        if teams == '':
            return
        manager.userperm.set_board_allow(self.boardname, teams)

    def handler_postteam(self, teams):
        if teams == '':
            return
        manager.userperm.set_board_post(self.boardname, teams)

    def handler_denyteam(self, teams):
        if teams == '':
            return
        manager.userperm.set_board_deny(self.boardname, teams)

    def handler_adminteam(self, teams):
        if teams == '':
            return
        manager.userperm.set_board_admin(self.boardname, teams)        

@mark('sys_update_boardattr_iter')
class EditBoardAttrIterFrame(EditBoardAttrFrame):

    def initialize(self):
        self.cls()
        boardname = self.readline(prompt=u'请输入版块的名称：')
        super(EditBoardAttrIterFrame, self).initialize(boardname)

@mark('sys_all_boards')
class AdminAllBoards(BaseBoardListFrame):

    def get_default_index(self):
        return 0

    def get_data(self, start, limit):
        return self.boards[start:start+limit]

    def initialize(self):
        self.sort_mode = 0
        self.boards = manager.board.get_all_boards()
        self.board_total = len(self.boards)
        super(AdminAllBoards, self).initialize()
    
    def change_board_attr(self):
        self.suspend('sys_set_boardattr', boardname=self.table.fetch()['boardname'])

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

@mark('sys_get_userid')
class GetUserIdFrame(BaseAuthedFrame):

    def initialize(self, callback, **kwargs):
        self.cls()
        userid = self.readline(prompt=u'请输入要管理的帐号：')
        if manager.userinfo.get_user(userid):
            self.goto(callback, userid=userid, **kwargs)
        else:
            self.writeln(u'没有该用户！')
            self.pause()
            self.goto_back()

@mark('sys_user_join_team')
class EditUserTeamFrame(BaseAuthedFrame):

    def initialize(self, userid, destteam):
        manager.team.join_team(userid, destteam)
        self.writeln(u'\r\n%s 加入了 %s 组' % (userid, destteam))
        self.pause()
        self.goto_back()

@mark('sys_get_teamname')
class GetTeamnameFrame(BaseAuthedFrame):

    def initialize(self, callback, **kwargs):
        self.cls()
        teamname = self.readline(prompt=u'请输入要管理的组名：')
        if manager.team.exists(teamname) :
            self.goto(callback, teamname=teamname, **kwargs)
        else:
            self.writeln(u'没有该组！')
            self.pause()
            self.goto_back()

@mark('sys_edit_team_members')
class EditTeamMmembersFrame(BaseAuthedFrame):

    def initialize(self, teamname):
        self.cls()
        self.teamname = teamname
        members = list(manager.team.all_members(teamname))
        self.render('top')
        self.write(''.join([ac.move2(2,1),
                            config.str['EDIT_LIST_QUICK_HELP'],
                           '\r\n',
                           config.str['EDIT_LIST_TEAM_THEAD']]))
        self.listbox = self.load(ListBox, start_line=4)
        self.listbox.update(members, members)
        self.prepare_remove = set()

    def get(self, char):
        if char in config.hotkeys['edit_list_ui']:
            getattr(self.listbox, config.hotkeys['edit_list_ui'][char])()
        elif char in config.hotkeys['edit_list'] :
            getattr(self, config.hotkeys['edit_list'][char])()

    def add(self):
        userids = self.readline(prompt=u'请输入要加入的id，逗号隔开：')
        if userids :
            succ = 0
            notfound = 0
            for u in userids.split(',') :
                user = manager.userinfo.get_user(u)
                if user :
                    manager.team.join_team(user['userid'], self.teamname)
                    succ += 1
                else:
                    notfound += 1
            self.hint(u'加入成功 %s 个，找不到id共 %s 个' % (succ, notfound))
        self.refresh_items()

    def remove(self):
        userid = self.listbox.fetch()
        self.prepare_remove.add(userid)
        self.write('                         ')
        self.listbox.fix_cursor()

    def refresh_items(self):
        if self.prepare_remove :
            for u in self.prepare_remove:
                manager.team.remove_team(u, self.teamname)
            self.prepare_remove.clear()
        members = list(manager.team.all_members(self.teamname))
        self.listbox.update(members, members)

    def hint(self, msg):
        self.writeln('%s%s' % (ac.move2(23, 1), msg))
        self.pause()

    def readline(self, prompt):
        return self.readline_safe(prompt='%s%s\r\n' % (ac.move2(21,1), prompt))

@mark('sys_edit_user_team')
class EditTeamMmembersFrame(BaseAuthedFrame):

    def initialize(self, userid):
        self.cls()
        self.euserid = userid
        teams = list(manager.team.user_teams(userid))
        self.render('top')
        self.write(''.join([ac.move2(2,1),
                            config.str['EDIT_LIST_QUICK_HELP'],
                           '\r\n',
                           config.str['EDIT_LIST_USERTEAM_THEAD']]))
        self.listbox = self.load(ListBox, start_line=4)
        self.listbox.update(teams, teams)
        self.prepare_remove = set()

    def get(self, char):
        if char in config.hotkeys['edit_list_ui']:
            getattr(self.listbox, config.hotkeys['edit_list_ui'][char])()
        elif char in config.hotkeys['edit_list'] :
            getattr(self, config.hotkeys['edit_list'][char])()

    alias = {
        "#0":"SYS_GUEST", "#1":"SYS_WELCOME", "#2":"SYS_USER",
        "#3":"SYS_SYSOPS", "#4":"SYS_SUPER",
        }

    def add(self):
        self.write(''.join([ac.move2(4, 1),
                            ac.kill_line_n(20),
                            ac.move2(5, 1),
                            self.render_str('add_team_hint')]))
        teams = self.readline(prompt=u'请输入要加入的组，逗号隔开：')
        if teams :
            succ = 0
            notfound = 0
            for t in teams.split(',') :
                if t in self.alias:
                    t = self.alias[t]
                if manager.team.exists(t) :
                    manager.team.join_team(self.euserid, t)
                    succ += 1
                else:
                    notfound += 1
            self.hint(u'加入成功 %s 个，找不到id共 %s 个' % (succ, notfound))
        self.refresh_items()

    def remove(self):
        teamname = self.listbox.fetch()
        self.prepare_remove.add(teamname)
        self.write('                         ')
        self.listbox.fix_cursor()

    def refresh_items(self):
        if self.prepare_remove :
            for t in self.prepare_remove:
                manager.team.remove_team(self.euserid, t)
            self.prepare_remove.clear()
        teams = list(manager.team.user_teams(self.euserid))
        self.listbox.update(teams, teams)

    def hint(self, msg):
        self.writeln('%s%s' % (ac.move2(23, 1), msg))
        self.pause()

    def readline(self, prompt):
        return self.readline_safe(prompt='%s%s\r\n' % (ac.move2(21,1), prompt))

@mark('sys_join_teams')
class JoinTeamsFrame(BaseAuthedFrame):

    def initialize(self, userid, teams):
        succ = 0
        notexists = 0
        for t in teams:
            if manager.team.exists(t) :
                manager.team.join_team(userid, t)
                succ += 1
            else:
                notexists += 1
        self.writeln(u' %s 加入 %s \r\n 成功 %s, 不存在的组 %s' % (userid, succ, notexists))
        self.pause()
        self.goto_back()

@mark('sys_set_board_deny')
class SetBoardDenyFrame(BaseAuthedFrame):

    def initialize(self, boardname):
        self.boardname = boardname
        self.cls()
        self.write(''.join([self.render_str('top'),
                            '\r\n',
                            config.str['DENY_QUICK_HELP'],
                            '\r\n',
                            config.str['DENY_THEAD']]))
        try:
            self.table = self.load(PagedTable, loader=self.get_data,
                                   formater=self.wrapper_li, start_num=0,
                                   start_line=4, height=18)
        except NullValueError as e:
            self.catch_nodata(e)
            self.goto_back()
        self.table.restore_screen()

    def get(self, char):
        if char in config.hotkeys['g_table'] :
            getattr(self.table, config.hotkeys['g_table'][char])()
        elif char in config.hotkeys['set_board_deny'] :
            getattr(self, config.hotkeys['set_board_deny'][char])()

    def get_data(self, start, limit):
        return manager.deny.get_denys(self.boardname, start, limit)

    def wrapper_li(self, record):
        return self.render_str('deny-li', **record)

    def _add_deny(self):
        userid = self.readline(prompt=u'[22;1H[K请输入欲封禁的id：')
        if not userid :
            raise ValueError(u'放弃操作')
        user = manager.userinfo.get_user(userid)
        if not user :
            raise ValueError(u'没有该id！')
        if manager.deny.get_deny(userid, self.boardname):
            raise ValueError(u'该id已经被封！')
        userid = user['userid']
        why = self.readline(prompt=u'\r[K请输入封禁的原因：')
        if not why or len(why) >= 128 :
            raise ValueError(u'不合法的输入或中止输入！')
        day = self.readline(prompt=u'\r[K请输入封禁天数：')
        if not day.isdigit() :
            raise ValueError(u'不合法的输入或中止输入！')
        day = int(day)
        if not ( 0 < day < 10):
            raise ValueError(u'封禁时间太长或不合理！')
            return
        start = datetime.datetime.now()
        free = start + datetime.timedelta(day)
        manager.admin.deny_user(self.userid, userid, self.boardname,
                                why, start, free)

    def add_deny(self):
        try:
            self._add_deny()
        except ValueError as e:
            self.hint('\r[K%s' % e.message) 
        self.reload()

    def remove_deny(self):
        record = self.table.fetch()
        confirm = self.readline(prompt=u'[22;1H[K确认解除封禁？ YES/else >> ')
        if confirm == 'YES':
            manager.admin.undeny_user(record['userid'], self.boardname)
            self.reload()
        else:
            self.hint(u' 取消操作')

    def hint(self, msg):
        self.write(msg)
        self.pause()
        self.table.restore_cursor_gently()

    def catch_nodata(self, e):
        self.write(u'\r\n现在没有封禁的帐号！')
        self.pause()
        try:
            self._add_deny()
        except ValueError as e:
            self.writeln(e.message)
        else:
            self.writeln(u' 成功！')
        self.pause()
        self.goto_back()

    def reload(self):
        try:
            self.table.reload()
        except TableLoadNoDataError as e:
            self.catch_nodata(e)
        else:
            self.table.restore_screen()

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

    def action_reload_config(self):
        reload(config)

    def action_reload(self, mod):
        import sys
        try:
            sys.modules[mod]
        except KeyError as e:
            raise ValueError(u'没有该模块！ [%s]' % mod)
        reload(sys.modules[mod])

    def reload_all(self):
        global ALL_BASE_MODULE
        global ALL_MODULES
        import sys
        for mod in ALL_MODULES :
            if mod not in ALL_BASE_MODULE :
                reload(sys.modules[mod])

    def action_show_modules(self, split=3):
        import sys
        mod = sys.modules.keys()
        formatc = '%%-%ds' % int(80/split)
        for d in list_split(mod, split):
            self.writeln(' ' .join(map(lambda x: formatc % x , d)))
            self.pause()
