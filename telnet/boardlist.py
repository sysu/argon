#!/usr/bin/python2
# -*- coding: utf-8 -*-

from chaofeng.g import mark
from chaofeng.ui import FinitePagedTable, NullValueError
import chaofeng.ascii as ac
from libframe import BaseAuthedFrame
from model import manager
import config

class BaseBoardListFrame(BaseAuthedFrame):

    def enter_board(self, board):
        self.suspend('_board_o', board=board)

    def query_board(self, board):
        self.suspend('_query_board_o', board=board)

    def query_user(self, board):
        self.suspend('query_user', userid=board['userid'])

    def change_board_attr(self, board):
        #####################   CHECK PERM HERE 
        self.suspend('sys_set_boardattr', boardname=board['boardname'])

    def catch_nodata(self):
        self.cls()
        self.pause_back(u'没有讨论区！')

    def add_to_fav(self, board):
        manager.favourite.add(self.userid, board[u'bid'])
        self.message(u'加入收藏夹成功！')

    def remove_fav(self, board):
        manager.favourite.remove(self.userid, board[u'bid'])
        self.message(u'移除收藏夹成功！')

    def set_readonly(self, board):
        self.message(u'努力地建设设置只读中！')

    def wrapper_board(self, board):
        board['online'] = manager.status.board_online(board['boardname'])
        return board

    def fgo_query_user_iter(self):
        self.suspend("query_user_iter")

    def fgo_get_mail(self):
        self.suspend("get_mail")

    def fgo_bye(self):
        self.suspend("bye")

    _SORT_KEY_FUNC = (
        lambda x : -x['bid'],
        lambda x : -int(manager.status.board_online(x['boardname']) or 0),
        lambda x : x['boardname'],
        lambda x : x['description'],
        )
    _SORT_MODE_COUNT = len(_SORT_KEY_FUNC)
    _TABEL_START_LINE = 4
    _TABEL_HEIGHT = 20

    def get(self, char):
        if char == ac.k_finish :
            self._fetch_board_do('enter_board')
        self.do_command(config.shortcuts['boardlist'].get(char))
        self._table.do_command(config.shortcuts['boardlist_ui'].get(char))
        if char in config.shortcuts['boardlist_fetch_do'] :
            self._fetch_board_do(config.shortcuts['boardlist_fetch_do'][char])

    def get_default_index(self, boards, default=0):
        userid = self.userid
        for index,b in enumerate(boards):
            if manager.readmark.is_new_board(userid, b['boardname']):
                return index
        else :
            return default

    def setup(self, boards, mode=0, default=None):
        self._boards = boards
        self._total = len(boards)
        if default is None:
            default = self.get_default_index(boards)
        try:
            self._table = self.load(FinitePagedTable, self._get_board_range,
                                    self._wrapper_li, self._get_total,
                                    start_num=default,
                                    start_line=self._TABEL_START_LINE,
                                    height=self._TABEL_HEIGHT)
        except NullValueError:
            self.catch_nodata()
            raise NullValueError
        if mode :
            if 0 < mode < self._SORT_MODE_COUNT :
                self._boards.sort(key=self._SORT_KEY_FUNC[mode], reverse=True)
            else :
                mode = 0
        self._sort_mode = mode
        self._init_screen()

    def message(self, msg):
        self.render('bottom_msg', message=msg)
        self._table.restore_cursor_gently()
        
    def _init_screen(self):
        self.cls()
        self.top_bar()
        self.push('\r\n')
        self.push(config.str['BOARDLIST_QUICK_HELP'])
        self.push('\r\n')
        self.push(config.str['BOARDLIST_THEAD'])
        self.bottom_bar()
        self._table.restore_screen()

    def restore(self):
        default = self.get_default_index(self._boards,
                                         self._table.fetch_num())
        try:
            try:
                self._table.setup(default)
            except NullValueError:
                if default !=0 :
                    self._table.setup(0)
        except NullValueError:
            self.catch_nodata()
            raise ValueError
        else:
            self._init_screen()

    def _get_board_range(self, start, limit):
        for index in range(len(self._boards[start:start+limit])):
            self._boards[start+index]['index'] = start+index
        return self._boards[start:start+limit]

    def _get_total(self):
        return self._total

    def _wrapper_li(self, board):
        board = self.wrapper_board(board)
        return self.render_str('boardlist-li', **board)

    def _goto_last(self):
        self._table.goto(self._total - 1)

    def _goto_line(self):
        self.push(u'[2;1H[K跳转到讨论区编号：')
        no = self.readnum()
        self.push('\r[K')
        self.push(config.str['BOARDLIST_QUICK_HELP'])
        if no is not False:
            self._table.goto(no)
        else:
            self._table.restore_cursor_gently()

    def _goto_with_prefix(self, prefix):
        data = self._boards
        prefix = prefix.lower()
        for index,item in enumerate(data):
            if item[u'boardname'].lower().startswith(prefix):
                self._table.restore_cursor_gently()
                self._table.goto(index)
                return True
        return False

    def _search(self):
        self.push(u'[2;1H[K搜寻讨论区：')
        self.read_with_hook(hook = lambda x : self._goto_with_prefix(x),
                            pos=[2,14])
        self.push(u'\r[K')
        self.push(config.str['BOARDLIST_QUICK_HELP'])
        self._table.restore_cursor_gently()

    def _change_sort(self):
        self._sort_mode += 1
        if 0 < self._sort_mode < self._SORT_MODE_COUNT :
            self._boards.sort(key=self._SORT_KEY_FUNC[self._sort_mode],
                              reverse=True)
        else:
            self._boards.sort(key=self._SORT_KEY_FUNC[0])
            self._sort_mode = 0
        self._table.goto(self._table.fetch_num())

    def _fetch_board_do(self, attrname):
        board = self._table.fetch()
        getattr(self, attrname)(board)
    
    def readline(self):
        self.push(ac.move2(24, 1))
        self.push(ac.kill_line)
        res = self.safe_readline()
        self.push(u'\r')
        self.push(self.render_str('bottom'))
        self._table.restore_cursor_gently()
        return res

@mark('boardlist')
class BoardListFrame(BaseBoardListFrame):

    def initialize(self, sid=None, default=None):
        manager.status.set_status(self.seid,
                                  manager.status.READBRD)
        boards = manager.query.get_boards(self.userid, sid)
        self.setup(boards, default=default)

@mark('favourite')
class FavouriteFrame(BaseBoardListFrame):

    def initialize(self, default=None):
        boards = manager.query.get_all_favourite(self.userid)
        self.setup(boards, default=default)
        
