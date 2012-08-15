#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import mark
from chaofeng.ui import PagedTable, NullValueError, TableLoadNoDataError
from model import manager
from libframe import BaseBoardListFrame,BaseTableFrame,BaseTextBoxFrame
from libtelnet import zh_format_d
from libdecorator import need_perm
import config

@mark('boardlist')
class NormalBoardListFrame(BaseBoardListFrame):

    def get_default_index(self):
        return 0

    def get_data(self, start, limit):
        return self.boards[start:start+limit]

    def load_boardlist(self):
        self.boards = manager.query.get_boards(self.userid, self.sid)
        self.board_total = len(self.boards)

    def catch_nodata(self, e):
        self.cls()
        self.writeln(u'没有讨论区！')
        self.pause()
        self.goto_back()

    def initialize(self, sid=None):
        self.sid = sid
        self.load_boardlist()
        self.sort_mode = 0
        super(NormalBoardListFrame, self).initialize()

    def change_board_attr(self):
        self.suspend('sys_set_boardattr', board=self.table.fetch())

@mark('favourite')
class FavouriteFrame(BaseBoardListFrame):

    def catch_nodata(self, e):
        self.cls()
        self.writeln(u'没有收藏任何版块！')
        self.pause()
        self.goto_back()

    def get_default_index(self):
        return 0

    def get_data(self, start, limit):
        return manager.query.get_all_favourite(self.userid)

    def show_help(self):
        self.suspend('help', page='boardlist')

@mark('board')
class BoardFrame(BaseTableFrame):

    def top_bar(self):
        self.writeln(self.render_str('top'))

    def quick_help(self):
        self.writeln(config.str['BOARD_QUICK_HELP'])

    def print_thead(self):
        self.write(self.thead)

    def notify(self, msg):
        self.write(ac.move2(0, 1))
        self.render('top_msg', messages=msg)
        self.table.restore_cursor_gently()

    def get_default_index(self):
        return 0

    def get_data(self, start, limit):
        return self.data_loader(start, limit)

    def wrapper_li(self, li):
        return self.render_str('board-li', **li)

    def get(self, data):
        print repr(data),data==ac.k_home
        if data in ac.ks_finish:
            self.finish()
        self.table.do_command(config.hotkeys['g_table'].get(data))
        self.table.do_command(config.hotkeys['board_table'].get(data))
        self.do_command(config.hotkeys['board'].get(data))

    def catch_nodata(self, e):
        self.cls()
        if self.readline_safe(prompt=u'没有文章，发表新文章？', buf_size=3) in ac.ks_yes :
            self.goto('new_post', board=self.board)
        else:
            self.goto_back()

    def check_perm(self, board):
        r = manager.query.get_board_ability(self.session.user.userid, board['boardname'])[0]
        self.authed = r
        return r or u'错误的讨论区或你无权力进入该版'

    @need_perm
    def initialize(self, board):
        self.board = board
        self.boardname = board['boardname']
        manager.action.enter_board(self.userid, self.seid, self.boardname)
        self.session.lastboard = board
        self._set_view_mode(0)
        super(BoardFrame, self).initialize()
                
    ##########

    def clear(self):
        if self.authed:
            manager.action.exit_board(self.userid, self.seid, self.boardname)

    mode_thead = ['NORMAL', 'GMODE', 'MMODE', 'TOPIC', 'ONETOPIC', 'AUTHOR']

    def _set_view_mode(self, mode):
        if mode == 1:
            data_loader = lambda o,l : manager.post.get_posts_g(self.boardname, o, l)
        elif mode == 2:
            data_loader = lambda o,l : manager.post.get_posts_m(self.boardname, o, l)
        elif mode == 3:
            data_loader = lambda p,l : manager.post.get_posts_topic(self.boardname, p, l)
        elif mode == 4:
            data_loader = lambda p,l : manager.post.get_posts_onetopic(self.tid, self.boardname,p,l)
        elif mode == 5:
            data_loader = lambda p,l : manager.post.get_posts_owner(self.author, self.boardname,p,l)
        else :
            data_loader = lambda o,l : manager.post.get_posts(self.boardname, o, l)
        self.data_loader = data_loader
        self.thead = config.str['BOARD_THEAD_%s' % self.mode_thead[mode]]
        self.mode = mode

    def set_view_mode(self, mode):
        self._set_view_mode(mode)
        try:
            self.table.load_data(0)
        except TableLoadNoDataError:
            self._set_view_mode(0)
            self.table.reload()
            self.restore()
        else:
            self.table.reload()
            self.restore()
            self.message(config.str['MSG_BOARD_MODE_%s' % self.mode_thead[self.mode]])

    def finish(self):
        pid = self.table.fetch()['pid']
        if pid is not None:
            self.suspend('post', board=self.board, pid=pid)

    #####################

    def goto_line(self):
        no = self.readnum(prompt=u"跳转到哪篇文章？")
        if no is not False:
            self.table.goto(no)
        else:
            self.table.refresh_cursor_gently()
            self.message(u'放弃输入')

    def get_last_pid(self):
        return manager.post.get_last_pid(self.boardname)

    def get_total(self):
        return manager.post.get_board_total(self.boardname)

    def goto_last(self):
        self.table.goto(self.get_total() -1)

    def change_mode(self):
        if self.mode >=3 : mode=0
        else : mode = self.mode+1
        self.set_view_mode(mode)
        # self.table.goto(0)  #!!!  Ugly but work.
        # self.restore()

    ###############
    # Edit/Reply  #
    ###############

    def new_post(self):
        self.suspend('new_post', board=self.board)

    def reply_post(self):
        p = self.table.fetch()
        self.suspend('reply_post', board=self.board, post=p)

    def edit_post(self):
        p = self.table.fetch()
        self.suspend('edit_post', board=self.board, post=p)

    def edit_title(self):
        p = self.table.fetch()
        title = self.readline(prompt=u'新标题：',prefix=p['title'])
        p['title'] = title
        manager.action.update_title(self.userid,self.boardname,
                                    p['pid'], title)
        self.table.set_hover_data(p)
        
#     def del_post(self):
#         pass

#     def reproduced(self):
#         pass

    def goto_tid(self):
        self.tid = self.table.fetch()['tid']
        self.set_view_mode(4)
        # self.table.goto(0)    #!!!! ugly too.
        # self.restore()

    def goto_author(self):
        self.author = self.table.fetch()['owner']
        self.set_view_mode(5)
        # self.table.goto(0)    #!!!! ugly too.
        # self.restore()

    def goto_back(self):
        if self.mode != 0 :
            self.set_view_mode(0)
            # self.restore()
            return
        super(BoardFrame, self).goto_back()

    def clear_readmark(self):
        last = self.get_last_pid()
        manager.readmark.clear_unread(self.userid, self.boardname, last)
        self.restore()

    def set_read(self):
        p = self.table.fetch()
        manager.readmark.set_read(self.userid, self.boardname, p['pid'])
        self.table.set_hover_data(p)

    def set_g_mark(self):
        p = self.table.fetch()
        p = manager.admin.set_g_mark(self.userid, self.board, self.post)
        self.set_hover_data(p)

    def set_m_mark(self):
        p = self.table.fetch()
        p = manager.admin.set_m_mark(self.userid, self.board, self.post)
        self.set_hover_data(p)

    def query_author(self):
        userid = self.table.fetch()['owner']
        user = manager.query.get_user(self.userid, userid)
        self.suspend('query_user', user=user)        

    def show_help(self):
        self.suspend('help', page='board')

@mark('query_board')
class QueryBoardFrame(BaseTextBoxFrame):

    def get_text(self):
        return self.render_str('board-t', **self.board)
    
    def initialize(self, board):
        self.board = board
        super(QueryBoardFrame, self).initialize()

    def finish(self,a=None):
        self.goto_back()

    def add_to_fav(self):
        manager.favourite.add(self.userid, self.board['bid'])
        self.message(u'预定版块成功！')

    def get(self, data):
        super(QueryBoardFrame, self).get(data)
        self.do_command(config.hotkeys['view-board'].get(data))
