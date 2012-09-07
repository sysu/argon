#!/usr/bin/python2
# -*- coding: utf-8 -*-

from chaofeng.g import mark
from chaofeng.ui import FinitePagedTable, NullValueError, TableLoadNoDataError
import chaofeng.ascii as ac
from libframe import BaseAuthedFrame
from model import manager
import config

class BasePostListFrame(BaseAuthedFrame):

    shortcuts = {}
    shortcuts_table = {}
    shortcuts_fetch_do = {}
    shortcuts_update = {}

    _TABEL_START_LINE = 4
    _TABEL_HEIGHT = 20

    def get(self, char):
        if char == ac.k_finish :
            self.fetch_post_do('next_frame')
        self.do_command(self.shortcuts.get(char))
        self._table.do_command(self.shortcuts_table.get(char))
        self.fetch_post_do(self.shortcuts_fetch_do.get(char))
        self.fetch_post_update(self.shortcuts_update.get(char))

    def _init_screen(self):
        self.cls()
        self.top_bar()
        self.push('\r\n')
        self.push(config.str['BOARD_QUICK_HELP'])
        self.push('\r\n')
        self.push(self._thead)
        self.bottom_bar()
        self._table.restore_screen()

    def setup(self, thead, dataloader, counter):
        default = self.get_default_index()
        try:
            self._table = self.load(FinitePagedTable, dataloader,
                                    self._wrapper_li, counter, default,
                                    start_line=self._TABEL_START_LINE,
                                    height=self._TABEL_HEIGHT)
        except NullValueError:
            self.catch_nodata()
            raise NullValueError
        self._thead = thead
        self._init_screen()

    def fetch_post_do(self, cmd):
        if cmd is None :
            return
        post = self._table.fetch()
        getattr(self, cmd)(post)

    def fetch_post_update(self, cmd):
        if cmd is None :
            return
        post = self._table.fetch()
        post = getattr(self, cmd)(post)
        if post is not None:
            self._table.set_hover_data(post)

    def reload(self):
        try:
            self._table.reload()
        except TableLoadNoDataError:
            self.goto_back()
        self._table.restore_screen()

    def restore(self):
        self._init_screen()

class BaseBoardFrame(BasePostListFrame):

    def top_bar(self):
        bm = self.board['bm']
        mid = u'○ %s' % self.boardname
        vis_len = ac.pice_width(mid)
        left = bm.replace(':', ',') if bm else u'诚征版主中'
        if self.session['lastboard'] :
            right = u'%s区 [%s]' % (self.session['lastsection'],
                                    self.session['lastboard'])
        else:
            right = u''
        if manager.notify.check_mail_notify(self.userid):
            tpl = 'top_board_notify'
        elif manager.notify.check_notice_notify(self.userid):
            tpl = 'top_board_notify_notice'
        else :
            tpl = 'top_board'
        self.render(tpl, left=left, mid=mid, right=right)

    def get_pid_rank(self, pid):
        raise NotImplementedError
                
    def setup(self, board, thead, dataloader, counter, default=0):
        self.board = board
        self.perm = board.perm
        self.boardname = board['boardname']
        super(BaseBoardFrame, self).setup(
            thead=thead, dataloader=dataloader, 
            counter=counter, 
            )
            
    def finish(self, post):
        self.suspend('post', boardname=self.boardname, pid=post['pid'])

    def get_default_index(self):
        return manager.telnet['default_board_index'].get('%s:%s' % (
                self.boardname, self.userid)) or 0

    def leave(self):
        if hasattr(self, '_table'):
            manager.telnet['default_board_index']['%s:%s' % (
                    self.boardname, self.userid)] = self._table.fetch_num()

    def restore(self):
        if self.session['board_flash'] :
            manager.telnet['default_board_index']['%s:%s' % (
                   self.boardname, self.userid)] = self.get_pid_rank(
                self.session['board_flash'])
        default = self.get_default_index()
        try:
            try:
                self._table.setup(default)
            except NullValueError:
                self._table.setup(0)
        except NullValueError:
            self.catch_nodata()
            raise ValueError
        self._init_screen()

    def new_post(self):
        self.suspend('new_post', boardname=self.boardname)

    def reply_post(self, post):
        self.suspend('_reply_post_o', boardname=self.boardname,
                     post=post)

    def reply_to_author(self, post):
        self.suspend('send_mail', touserid=post['owner'])

    def set_replyable(self, post):
        if post.owner == self.userid :
            post['replyable'] = not post['replyable']
            manager.admin.set_post_replyattr(self.userid, self.boardname,
                                             post['pid'], post['replyable'])
            return post

    def edit_post(self, post):
        self.suspend('_edit_post_o', board=self.board, post=post)

    def edit_title(self, post):
        if post.owner == self.userid :
            title = self.readline(prompt=u'新标题：',prefix=post['title'])
            if not title:
                self.message(u'放弃操作')
                return
            post['title'] = title
            manager.action.update_title(self.userid,self.boardname,
                                        post['pid'], title)
            return post
        else:
            self.message(u'你没有该权限！')

    def del_post(self, post):
        if post['owner'] == self.userid :
            if self.readline(buf_size=1,prompt=u"删除你的文章?[y/n] ") in ac.ks_yes : 
                manager.admin.remove_post_personal(self.userid, self.boardname, post['pid'])
                self.reload()
                self.message(u'自删成功')
        elif self.perm[3] :
            if self.readline(buf_size=1,prompt=u'将文章放入废纸篓？[y/n] ') in ac.ks_yes :
                manager.admin.remove_post_junk(self.userid, self.boardname, post['pid'])
                self.reload()
                self.message(u'删贴成功')

    def set_read(self, post):
        manager.readmark.set_read(self.userid, self.boardname, p['pid'])
        return post

    def set_g_mark(self, post):
        return manager.admin.set_g_mark(self.userid, self.board, post)        

    def set_m_mark(self, post):
        return manager.admin.set_m_mark(self.userid, self.board, post)

    def goto_query_user(self, post):
        self.suspend('query_user', userid=post['owner'])

    def goto_set_deny(self):
        if self.perm[3] :
            self.suspend('sys_set_board_deny', boardname=self.boardname)
        
    def _wrapper_li(self, post):
        return self.render_str('board-li',
                               readmark=manager.readmark.is_read(self.userid,
                                                                 self.boardname,
                                                                 post['pid']),
                               **post)

    def _goto_line(self):
        no = self.readnum(prompt=u'跳转到哪篇文章？')
        if no is not False:
            self._table.goto(no)
        else:
            self._table.restore_cursor_gently()

    def message(self, msg):
        self.render('bottom_msg', message=msg)
        self._table.restore_cursor_gently()

    def readline(self, prompt=u'', prefix=u'', acceptable=ac.is_safe_char,
                 buf_size=20):
        self.push(ac.move2(24, 1))
        self.push(ac.kill_line)
        res = self.safe_readline(prompt=prompt, prefix=prefix,
                                 acceptable=acceptable, buf_size=buf_size)
        self.push(u'\r')
        self.push(self.render_str('bottom'))
        self._table.restore_cursor_gently()
        return res

    _ALL_FILTER_MODE = set(('g', 'm', 'o'))
    def goto_filter_mode(self):
        mode  = self.readline(prompt=u'g) 文摘 m) 美文 o) 主题折叠', buf_size=3)
        if mode in self._ALL_FILTER_MODE:
            self.suspend('_board_filter_o', board=self.board, mode=mode)

    def goto_filter_g(self):
        self.suspend('_board_filter_o', board=self.board, mode='g')

    def goto_filter_tid(self):
        self.suspend('_board_filter_o', board=self.board, mode='t',
                     tid=self._table.fetch()['tid'])

    def goto_filter_author(self):
        self.suspend('_board_filter_o', board=self.board, mode='u',
                     owner=self._table.fetch()['owner'])

@mark('_board_o')
class BoardFrame(BaseBoardFrame):

    THEAD = config.str['BOARD_THEAD']
    shortcuts = config.shortcuts['board']
    shortcuts_table = config.shortcuts['board_ui']
    shortcuts_fetch_do = config.shortcuts['board_fetch']
    shortcuts_update = config.shortcuts['board_update']

    def next_frame(self, post):
        self.suspend('_view_post_o', post=post)

    def initialize(self, board, default=0):
        dataloader = manager.post.get_posts_loader(board['boardname'])
        counter = manager.post.get_posts_counter(board['boardname'])
        self.session['last_board_attr'] = board
        self.setup(board, self.THEAD, dataloader, counter, default)

    def get_pid_rank(self, pid):
        return manager.post.get_rank_num(self.boardname, pid)
    
    def catch_nodata(self):
        self.cls()
        if self.confirm(u'没有文章！是否发表新文章？[y/n]：', default='y') :
            self.goto('new_post', boardname=self.board['boardname'])
        else:
            self.pause_back(u'放弃操作')

    def change_board(self):
        boardname = self.readline(prompt=u'请输入要切换的版块：')
        board = manager.board.get_board(boardname)
        if board :
            self.goto('_board_o', board=board)
        else:
            self.message(u'没有该讨论区！')

    def del_post_range(self):
        if self.perm[3] :
            start = self.readline(prompt=u'首篇文章编号: ')
            if start.isdigit() :
                end = self.readline(prompt=u'末篇文章编号：')
                if end.isdigit() :
                    start_num = manager.query.post_index2pid(self.boardname, int(start)-1)
                    end_num = manager.query.post_index2pid(self.boardname, int(end))
                    if start_num >= end_num :
                        self.message(u'错误的区间')
                        return
                    manager.admin.remove_post_junk_range(self.userid, self.boardname, start_num, end_num)
                    self.reload()
                else:
                    self.message(u'错误的输入')
            else:
                self.message(u'错误的输入')

    def clear_readmark(self):
        last = manager.post.get_last_pid(self.boardname)
        manager.readmark.clear_unread(self.userid, self.boardname, last)
        self.reload()

@mark('_board_filter_o')
class BoardFilterPostFrame(BaseBoardFrame):

    shortcuts = config.shortcuts['board_filter']
    shortcuts_table = config.shortcuts['board_ui']
    shortcuts_fetch_do = config.shortcuts['board_fetch']
    shortcuts_update = config.shortcuts['board_update']

    def catch_nodata(self):
        self.cls()
        self.pause_back(u'没有符合条件的文章！')

    ALL_MODE = {
        "g": lambda : manager.post.FILTER_G,
        "m": lambda : manager.post.FILTER_M,
        "o": lambda : manager.post.FILTER_O,
        "t": lambda tid : manager.post.sql_filter_tid(tid),
        "u": lambda owner : manager.post.sql_filter_owner(owner),
        }

    def get_pid_rank(self, pid):
        return manager.post.get_rank_num_cond(self.boardname,
                                              pid,
                                              self.cond)

    def initialize(self, board, mode, default=0, **kwargs):
        self.cond = self.ALL_MODE[mode](**kwargs)
        print self.cond
        dataloader = manager.post.get_posts_loader(board['boardname'],
                                                   self.cond)
        counter = manager.post.get_posts_counter(board['boardname'],
                                                 self.cond)
        thead = config.str['BOARD_%s_MODE_THEAD' % mode]
        self.setup(board, thead, dataloader, counter, default)

@mark('board')
class BoardFrame(BaseAuthedFrame):

    def initialize(self, boardname, prev, default=0):
        board = manager.query.get_board_by_name(boardname)
        self.goto('_board_o', board, prev, default)

