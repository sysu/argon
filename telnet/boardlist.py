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
        self.suspend('_sys_set_board_attr_o', board=board)

    def catch_nodata(self):
        self.cls()
        self.pause_back(u'没有讨论区！')

    def add_to_fav(self, board):
        manager.favourite.add(self.userid, board[u'bid'])
        self.message(u'加入收藏夹成功！')

    def remove_fav(self, board):
        manager.favourite.remove(self.userid, board[u'bid'])
        self.message(u'移除收藏夹成功！')

    def wrapper_board(self, board):
        board['online'] = manager.status.board_online(board['boardname'])
        return board

    def fgo_query_user_iter(self):
        self.suspend("query_user_iter")

    def fgo_get_mail(self):
        self.suspend("get_mail")

    def fgo_finish(self):
        self.goto("finish")

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

    def get_default_index(self, boards):
        userid = self.userid
        for index,b in enumerate(boards):
            if manager.readmark.is_new_board(userid, b['boardname']):
                default = index
                break
        else:
            default = 0

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
        if self.session['boardlist_flash'] :
            mode,default = self.session['boardlist_flash']
            self.session.pop('boardlist_flash')
            if 0 <= mode < self._SORT_MODE_COUNT :
                self._boards.sort(key=self._SORT_KEY_FUNC[mode],
                                  reverse=True)
            else :
                mode = 0
        else:
            default = self.get_default_index(self._boards)
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
        return self._boards[start:start+limit]

    def _get_total(self):
        return self._total

    def _wrapper_li(self, board):
        board = self.wrapper_board(board)
        return self.render_str('boardlist-li', **board)

    def _goto_last(self):
        self._table.goto(self._total - 1)

    def _goto_line(self):
        no = self.readnum()
        if no is not False:
            self._table.goto(no)
        else:
            self._table.refresh_cursor_gently()

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
        self.read_with_hook(hook = lambda x : self.goto_with_prefix(x),
                            prompt=u'搜寻讨论区：')
        self._table.restore_cursor_gently()

    def _change_sort(self):
        print self._sort_mode
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
        boards = manager.query.get_boards(self.userid, sid)
        self.setup(boards, default=default)

@mark('favourite')
class FavouriteFrame(BaseBoardListFrame):

    def initialize(self, default=None):
        boards = manager.query.get_all_favourite(self.userid)
        self.setup(boards, default=default)
        
# @mark('board')
# class BoardFrame(BaseTableFrame):

#     '''
#     use session['last_board_hover']
#     '''

#     def top_bar(self):
#         bm = self.board['bm']
#         mid = u'○ %s' % self.board['boardname']
#         vis_len = ac.pice_width(mid)
#         left = bm.replace(':', ',') if bm else u'诚征版主中'
#         if self.session['lastboard'] :
#             right = u'%s区 [%s]' % (self.session['lastsection'],
#                                     self.session['lastboard'])
#         else:
#             right = u''
#         if manager.notify.check_mail_notify(self.userid):
#             tpl = 'top_board_notify'
#         elif manager.notify.check_notice_notify(self.userid):
#             tpl = 'top_board_notify_notice'
#         else :
#             tpl = 'top_board'
#         self.render(tpl, left=left, mid=mid, right=right)

#     def quick_help(self):
#         self.writeln(config.str['BOARD_QUICK_HELP'])

#     def print_thead(self):
#         self.write(self.thead)

#     def notify(self, msg):
#         self.write(ac.move2(0, 1))
#         self.render('top_msg', messages=msg)
#         self.table.restore_cursor_gently()

#     def get_default_index(self):
#         return self.default

#     def get_data(self, start, limit):
#         return self.data_loader(start, limit)

#     def get_total(self):
#         raise NotImplementedError # rewrite in set mode

#     def wrapper_li(self, li):
#         return self.render_str('board-li', **li)

#     def get(self, data):
#         if data in ac.ks_finish:
#             self.finish()
#         self.table.do_command(config.hotkeys['g_table'].get(data))
#         self.table.do_command(config.hotkeys['board_table'].get(data))
#         self.do_command(config.hotkeys['board'].get(data))

#     def catch_nodata(self, e):
#         self.cls()
#         if self.readline_safe(prompt=u'没有文章，发表新文章？', buf_size=3) in ac.ks_yes :
#             self.goto('new_post', board=self.board)
#         else:
#             self.goto_back()

#     def check_perm(self, board, default=0):
#         board['perm'] = manager.query.get_board_ability(self.session.user.userid, board['boardname'])
#         r = board.perm[0]
#         self.authed = r
#         return r or u'错误的讨论区或你无权力进入该版'

#     @need_perm
#     def initialize(self, board, default=0):
#         self.authed = True
#         self.perm = manager.query.get_board_ability(self.userid, board['boardname'])
#         self.board = board
#         self.boardname = board['boardname']
#         manager.action.enter_board(self.seid, self.boardname)  ### aother entance in view.py/51
#         self.session['lastboard'] = board['boardname']
#         self.session['lastsection'] = board['sid']
#         self._set_view_mode(0)
#         self.default = default
#         super(BoardFrame, self).initialize()

#     ##########

#     def clear(self):
#         if hasattr(self, 'authed'):
#             manager.action.exit_board(self.seid, self.boardname)

#     mode_thead = ['NORMAL', 'GMODE', 'MMODE', 'TOPIC', 'ONETOPIC', 'AUTHOR']

#     def _set_view_mode(self, mode):
#         if mode == 1:
#             data_loader = lambda o,l : manager.post.get_posts_g(self.boardname, o, l)
#             size_loader = lambda : manager.post.get_posts_g_total(self.boardname)
#         elif mode == 2:
#             data_loader = lambda o,l : manager.post.get_posts_m(self.boardname, o, l)
#             size_loader = lambda : manager.post.get_posts_m_total(self.boardname)
#         elif mode == 3:
#             data_loader = lambda p,l : manager.post.get_posts_topic(self.boardname, p, l)
#             size_loader = lambda : manager.post.get_posts_topic_total(self.boardname)
#         elif mode == 4:
#             data_loader = lambda p,l : manager.post.get_posts_onetopic(self.tid, self.boardname,p,l)
#             size_loader = lambda : manager.post.get_posts_onetopic_total(self.tid, self.boardname,)
#         elif mode == 5:
#             data_loader = lambda p,l : manager.post.get_posts_owner(self.author, self.boardname,p,l)
#             size_loader = lambda : manager.post.get_posts_owner_total(self.author, self.boardname)
#         else :
#             data_loader = lambda o,l : manager.post.get_posts(self.boardname, o, l)
#             size_loader = lambda : manager.post.get_posts_total(self.boardname)
#             mode = 0
#         self.data_loader = data_loader
#         self.get_total = size_loader
#         self.thead = config.str['BOARD_THEAD_%s' % self.mode_thead[mode]]
#         self.mode = mode

#     def set_view_mode(self, mode):
#         old_mode = self.mode
#         self._set_view_mode(mode)
#         try:
#             self.table.load_data(0)
#         except TableLoadNoDataError:
#             self._set_view_mode(old_mode)
#         else:
#             # self.table.reload()
#             self.restore()
#             self.message(config.str['MSG_BOARD_MODE_%s' % self.mode_thead[self.mode]])

#     def finish(self):
#         pid = self.table.fetch()['pid']
#         if pid is not None:
#             self.goto('post', boardname=self.board.boardname, pid=pid)

#     #####################

#     def goto_line(self):
#         no = self.readnum(prompt=u"跳转到哪篇文章？")
#         if no is not False:
#             self.table.goto(no)
#         else:
#             self.table.restore_cursor_gently()
#             self.message(u'放弃输入')

#     def change_board(self):
#         boardname = self.readline(prompt=u'请输入要切换的版块：')
#         board = manager.board.get_board(boardname)
#         if board :
#             perm = manager.query.get_board_ability(self.session.user.userid, board['boardname'])[0]
#             if perm :
#                 self.goto('board', board=board)
#         self.message(u'错误的讨论区或你无权力进入该版')

#     def query_user(self):
#         self.suspend('query_user_iter')
        
#         ####################

#     def get_last_pid(self):
#         return manager.post.get_last_pid(self.boardname)

#     def get_total(self):
#         return manager.post.get_board_total(self.boardname)

#     def goto_last(self):
#         self.table.goto(self.get_total() -1)

#     input_mode_map = {
#         "1":1, "2":2, "3":3, "0":0,
#         }
#     def change_mode(self):
#         s = self.readline(prompt=u'0)一般模式 1) 文摘 2)被m文章 3)同主题折叠 ', acceptable=ac.isdigit)
#         if s in self.input_mode_map :
#             self.set_view_mode(self.input_mode_map[s])
#         # self.table.goto(0)  #!!!  Ugly but work.
#         # self.restore()

#     def set_g_mode(self):
#         self.set_view_mode(1)

#     def set_onetopic_mode(self):
#         self.set_view_mode(0 if self.mode else 3)

#     def goto_bye(self):
#         self.goto('finish')
        
#     ###############
#     # Edit/Reply  #
#     ###############

#     def new_post(self):
#         self.suspend('new_post', board=self.board)

#     def reply_to_author(self):
#         p = self.table.fetch()
#         self.suspend('send_mail', touserid=p['owner'])

#     def set_replyable(self):
#         p = self.table.fetch()
#         if p.owner == self.userid :   ######### check perm
#             p['replyable'] = not p['replyable']
#             manager.admin.set_post_replyattr(self.userid, self.boardname,
#                                              p.pid, p.replyable)
#             self.table.set_hover_data(p)            

#     def edit_post(self):
#         p = self.table.fetch()
#         self.suspend('edit_post', board=self.board, post=p)

#     def edit_title(self):
#         p = self.table.fetch()
#         if p.owner == self.userid :  #######  need to check perm
#             title = self.readline(prompt=u'新标题：',prefix=p['title'])
#             if not title:
#                 self.message(u'放弃操作')
#                 return
#             p['title'] = title
#             manager.action.update_title(self.userid,self.boardname,
#                                         p['pid'], title)
#             self.table.set_hover_data(p)
#         else:
#             self.message(u'你没有该权限！')

#     def del_post(self):
#         p = self.table.fetch()
#         if p['owner'] == self.userid :
#             if self.readline(buf_size=1,prompt=u"删除你的文章?[y/n] ") in ac.ks_yes : 
#                 manager.admin.remove_post_personal(self.userid, self.boardname, p['pid'])
#                 self.restore()
#                 self.message(u'自删成功')
#         elif self.perm[3] :
#             if self.readline(buf_size=1,prompt=u'将文章放入废纸篓？[y/n] ') in ac.ks_yes :
#                 manager.admin.remove_post_junk(self.userid, self.boardname, p['pid'])
#                 self.restore()
#                 self.message(u'删贴成功')

#     def del_post_range(self):
#         if self.perm[3] :
#             start = self.readline(prompt=u'首篇文章编号: ')
#             if start.isdigit() :
#                 end = self.readline(prompt=u'末篇文章编号：')
#                 if end.isdigit() :
#                     start_num = manager.query.post_index2pid(self.boardname, int(start)-1)
#                     end_num = manager.query.post_index2pid(self.boardname, int(end))
#                     if start_num >= end_num :
#                         self.message(u'错误的区间')
#                         return
#                     manager.admin.remove_post_junk_range(self.userid, self.boardname, start_num, end_num)
#                     self.restore()
#                 else:
#                     self.message(u'错误的输入')
#             else:
#                 self.message(u'错误的输入')

#     def goto_tid(self):
#         self.tid = self.table.fetch()['tid']
#         self.set_view_mode(4)
#         # self.table.goto(0)    #!!!! ugly too.
#         # self.restore()

#     def goto_author(self):
#         self.author = self.table.fetch()['owner']
#         self.set_view_mode(5)
#         # self.table.goto(0)    #!!!! ugly too.
#         # self.restore()

#     def goto_back(self):
#         if hasattr(self, 'mode') and self.mode != 0 :
#             self.set_view_mode(0)
#             # self.restore()
#             return
#         super(BoardFrame, self).goto_back()

#     def clear_readmark(self):
#         last = self.get_last_pid()
#         manager.readmark.clear_unread(self.userid, self.boardname, last)
#         self.restore()

#     def set_read(self):
#         p = self.table.fetch()
#         manager.readmark.set_read(self.userid, self.boardname, p['pid'])
#         self.table.set_hover_data(p)

#     def check_admin_perm(self):
#         pass

#     def set_g_mark(self):
#         p = self.table.fetch()
#         p = manager.admin.set_g_mark(self.userid, self.board, p)
#         self.table.set_hover_data(p)

#     def set_m_mark(self):
#         p = self.table.fetch()
#         p = manager.admin.set_m_mark(self.userid, self.board, p)
#         self.table.set_hover_data(p)

#     def query_author(self):
#         userid = self.table.fetch()['owner']
#         self.suspend('query_user', userid=userid)        

#     def show_help(self):
#         self.suspend('help', page='board')

#     def set_deny(self):
#         if manager.query.get_board_ability(self.session.user.userid, self.boardname)[3] :
#             self.suspend('sys_set_board_deny', boardname=self.boardname)

# @mark('query_board')
# class QueryBoardFrame(BaseTextBoxFrame):

#     def get_text(self):
#         return self.render_str('board-t', **self.board)
    
#     def initialize(self, board):
#         self.board = board
#         super(QueryBoardFrame, self).initialize()

#     def finish(self,a=None):
#         self.goto_back()

#     def add_to_fav(self):
#         manager.favourite.add(self.userid, self.board['bid'])
#         self.message(u'预定版块成功！')

#     def get(self, data):
#         super(QueryBoardFrame, self).get(data)
#         self.do_command(config.hotkeys['view-board'].get(data))
