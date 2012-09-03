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

class BaseTableFrame(BaseAuthedFrame):

    ### Handler

    def quick_help(self):
        raise NotImplementedError
    
    def print_thead(self):
        raise NotImplementedError

    def notify(self, msg):
        raise NotImplementedError

    def get_default_index(self):
        raise NotImplementedError

    def get_data(self, start, limit):
        raise NotImplementedError

    def wrapper_li(self, li):
        raise NotImplementedError
    
    def get_total(self):
        raise NotImplementedError

    def catch_nodata(self, e):
        raise NotImplementedError(u'What to do while cannot catch anything [%s] ' % e.message)

    def load_table(self):
        try:
            return self.load(FinitePagedTable, self.get_data, self.wrapper_li,
                             get_last=self.get_total,
                             start_num=self.get_default_index(),
                             start_line=4, height=20)
        except NullValueError as e:
            self.catch_nodata(e)
            self.goto_back()
                           
    def initialize(self):
        super(BaseTableFrame, self).initialize()
        self.table = self.load_table()
        self.init_screen()

    def bottom_bar(self):
        self.render(u'bottom')

    def message(self, msg):
        self.session.message = msg
        self.write(ac.move2(24, 1))
        self.render(u'bottom_msg', message=msg)
        self.table.restore_cursor_gently()
        
    def init_screen(self):
        self.cls()
        self.top_bar()
        self.push('\r\n')
        self.quick_help()
        self.print_thead()
        self.bottom_bar()
        self.table.restore_screen()

    def restore(self):
        try:
            # self.table.reload()        ###############   Ugly!!!
            self.table.goto(self.get_default_index())
        except TableLoadNoDataError:
            self.goto_back()
        else:
            self.init_screen()

    def get(self, data):
        if data in ac.ks_finish:
            self.finish()
        self.table.do_command(config.hotkeys['table_table'].get(data))
        self.do_command(config.hotkeys['table'].get(data))

    def read_lbd(self, reader):
        u'''
        Wrapper real read function.
        '''
        self.write(u''.join((ac.move2(24,1),  ac.kill_line)))
        res = reader()
        self.write(u'\r')
        self.bottom_bar()
        self.table.restore_cursor_gently()
        return res

    def readline(self, acceptable=ac.is_safe_char, finish=ac.ks_finish,\
                     buf_size=20, prompt=u'', prefix=u''):
        return self.read_lbd(lambda : super(BaseTableFrame, self).\
                                 readline(acceptable, finish, 
                                          buf_size, prompt, prefix=prefix))

    def readnum(self, prompt=u''):
        no = self.readline(acceptable=lambda x:x.isdigit(),
                           buf_size=8,  prompt=prompt)
        if no :
            return int(no) - 1
        else :
            return False

    def read_with_hook(self, hook, buf_size=20, prompt=u''):
        self.write(u''.join((ac.move2(2,1),
                            ac.kill_line)))
        if prompt:
            self.write(prompt)
        buf = []
        while len(buf) < buf_size:
            ds = self.read_secret()
            ds = ds or ds[0]
            if ds == ac.k_backspace:
                if buf:
                    data = buf.pop()
                    self.write(ac.backspace)
                continue
            elif ds in ac.ks_finish:
                break
            elif ds == ac.k_ctrl_c:
                buf = False
                break
            else:
                if ds.isalnum() :
                    buf.append(ds)
                    self.write(ds)
                    hook(u''.join(buf))
        self.write(u'\r')
        self.quick_help()
        self.table.restore_cursor_gently()
        if buf is False :
            return buf
        else:
            return u''.join(buf)                
    
class BaseBoardListFrame(BaseTableFrame):

    boards = []

    # def top_bar(self):
    #     self.render('top')
    #     self.writeln()
        
    def quick_help(self):
        self.writeln(config.str[u'BOARDLIST_QUICK_HELP'])

    def print_thead(self):
        self.writeln(config.str[u'BOARDLIST_THEAD'])

    def notify(self, msg):
        self.write(ac.move2(0, 1))
        self.render(u'top_msg', messages=msg)
        self.table.restore_cursor_gently()

    def get_default_index(self):
        raise NotImplementedError

    def get_data(self, start, limit):
        raise NotImplementedError
    
    def wrapper_li(self, li):
        return self.render_str(u'boardlist-li', **li)

    def get(self, data):
        if data in ac.ks_finish:
            self.finish()
        self.table.do_command(config.hotkeys['g_table'].get(data))
        self.table.do_command(config.hotkeys['boardlist_table'].get(data))
        self.do_command(config.hotkeys['boardlist'].get(data))
        if data in config.hotkeys['boardlist_jump']:
            self.suspend(config.hotkeys['boardlist_jump'][data])
            
    def finish(self):
        self.suspend(u'board', board=self.table.fetch())
    
    def catch_nodata(self, e):
        self.cls()
        self.writeln(u'没有讨论区！')
        self.pause()
        self.goto_back()

    ######################

    def goto_last(self):
        self.table.goto(self.board_total-1)

    def goto_line(self):
        no = self.readnum()
        if no is not False:
            self.table.goto(no)
        else:
            self.table.refresh_cursor_gently()
            self.message(u'放弃输入')

    def goto_with_prefix(self,prefix):  # // Ugly but work.
        data = self.boards
        prefix = prefix.lower()
        for index,item in enumerate(data):
            if item[u'boardname'].lower().startswith(prefix):
                self.write(ac.save)
                self.table.restore_cursor_gently()
                self.table.goto(index)
                self.write(ac.restore)
                return
            
    def search(self):
        self.read_with_hook(hook = lambda x : self.goto_with_prefix(x) ,
                            prompt=u'搜寻讨论区：')
        self.table.restore_cursor_gently()

    def sort(self, mode):
        if mode == 1 :
            self.boards.sort(key = lambda x: \
                                 manager.status.board_online(x[u'boardname'] \
                                                                 or 0),
                            reverse=True)
        elif mode == 2:
            self.boards.sort(key = lambda x: x[u'boardname'])
        elif mode == 3:
            self.boards.sort(key = lambda x: x[u'description'])
        else:
            self.boards.sort(key = lambda x:x[u'bid'])
        self.table.goto(self.table.fetch_num())

    def change_sort(self):
        self.sort_mode += 1
        if self.sort_mode > 3 :
            self.sort_mode = 0
        self.sort(self.sort_mode)
        self.restore()
        self.message(config.str[u'MSG_BOARDLIST_MODE_%s'%self.sort_mode])

    def watch_board(self):
        self.suspend(u'query_board', board=self.table.fetch())

    def add_to_fav(self):
        manager.favourite.add(self.userid, self.table.fetch()[u'bid'])
        self.message(u'预定版块成功！')

    def remove_fav(self):
        manager.favourite.remove(self.userid, self.table.fetch()[u'bid'])
        self.message(u'取消预定版块成功！')

    def show_help(self):
        self.suspend('help', page='boardlist')


@mark('boardlist')
class NormalBoardListFrame(BaseBoardListFrame):

    def get_default_index(self):
        userid = self.userid
        for index, b in enumerate(self.boards):
            if manager.readmark.is_new_board(userid, b['boardname']):
                return index
        if hasattr(self, 'table'):
            return self.table.fetch_num()
        return 0

    def get_data(self, start, limit):
        return self.boards[start:start+limit]

    def get_total(self):
        return self.board_total

    def load_boardlist(self):
        self.boards = manager.query.get_boards(self.userid, self.sid)
        self.board_total = len(self.boards)

    def initialize(self, sid=None):
        self.sid = sid
        self.load_boardlist()
        self.sort_mode = 0
        super(NormalBoardListFrame, self).initialize()

    def change_board_attr(self):
        boardname = self.table.fetch()['boardname']
        if manager.query.get_board_ability(self.userid, boardname)[3]:
            self.suspend('sys_set_boardattr', boardname=boardname)

@mark('favourite')
class FavouriteFrame(BaseBoardListFrame):

    def catch_nodata(self, e):
        self.cls()
        self.writeln(u'没有收藏任何版块！')
        self.pause()
        self.goto_back()

    def get_default_index(self):
        userid = self.userid
        for index, b in enumerate(self.data):
            if manager.readmark.is_new_board(userid, b['boardname']):
                return index
        if hasattr(self, 'table'):
            return self.table.fetch_num()
        return 0

    def get_data(self, start, limit):
        return self.data[start:start+limit]

    def get_total(self):
        return self.board_total

    def show_help(self):
        self.suspend('help', page='boardlist')

    def initialize(self):
        self.data = manager.query.get_all_favourite(self.userid)
        self.board_total = len(self.data)
        super(FavouriteFrame, self).initialize()
        
@mark('board')
class BoardFrame(BaseTableFrame):

    '''
    use session['last_board_hover']
    '''

    def top_bar(self):
        bm = self.board['bm']
        mid = u'○ %s' % self.board['boardname']
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

    def quick_help(self):
        self.writeln(config.str['BOARD_QUICK_HELP'])

    def print_thead(self):
        self.write(self.thead)

    def notify(self, msg):
        self.write(ac.move2(0, 1))
        self.render('top_msg', messages=msg)
        self.table.restore_cursor_gently()

    def get_default_index(self):
        return self.default

    def get_data(self, start, limit):
        return self.data_loader(start, limit)

    def get_total(self):
        raise NotImplementedError # rewrite in set mode

    def wrapper_li(self, li):
        return self.render_str('board-li', **li)

    def get(self, data):
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

    def check_perm(self, board, default=0):
        board['perm'] = manager.query.get_board_ability(self.session.user.userid, board['boardname'])
        r = board.perm[0]
        self.authed = r
        return r or u'错误的讨论区或你无权力进入该版'

    @need_perm
    def initialize(self, board, default=0):
        self.authed = True
        self.perm = manager.query.get_board_ability(self.userid, board['boardname'])
        self.board = board
        self.boardname = board['boardname']
        manager.action.enter_board(self.seid, self.boardname)  ### aother entance in view.py/51
        self.session['lastboard'] = board['boardname']
        self.session['lastsection'] = board['sid']
        self._set_view_mode(0)
        self.default = default
        super(BoardFrame, self).initialize()

    ##########

    def clear(self):
        if hasattr(self, 'authed'):
            manager.action.exit_board(self.seid, self.boardname)

    mode_thead = ['NORMAL', 'GMODE', 'MMODE', 'TOPIC', 'ONETOPIC', 'AUTHOR']

    def _set_view_mode(self, mode):
        if mode == 1:
            data_loader = lambda o,l : manager.post.get_posts_g(self.boardname, o, l)
            size_loader = lambda : manager.post.get_posts_g_total(self.boardname)
        elif mode == 2:
            data_loader = lambda o,l : manager.post.get_posts_m(self.boardname, o, l)
            size_loader = lambda : manager.post.get_posts_m_total(self.boardname)
        elif mode == 3:
            data_loader = lambda p,l : manager.post.get_posts_topic(self.boardname, p, l)
            size_loader = lambda : manager.post.get_posts_topic_total(self.boardname)
        elif mode == 4:
            data_loader = lambda p,l : manager.post.get_posts_onetopic(self.tid, self.boardname,p,l)
            size_loader = lambda : manager.post.get_posts_onetopic_total(self.tid, self.boardname,)
        elif mode == 5:
            data_loader = lambda p,l : manager.post.get_posts_owner(self.author, self.boardname,p,l)
            size_loader = lambda : manager.post.get_posts_owner_total(self.author, self.boardname)
        else :
            data_loader = lambda o,l : manager.post.get_posts(self.boardname, o, l)
            size_loader = lambda : manager.post.get_posts_total(self.boardname)
            mode = 0
        self.data_loader = data_loader
        self.get_total = size_loader
        self.thead = config.str['BOARD_THEAD_%s' % self.mode_thead[mode]]
        self.mode = mode

    def set_view_mode(self, mode):
        old_mode = self.mode
        self._set_view_mode(mode)
        try:
            self.table.load_data(0)
        except TableLoadNoDataError:
            self._set_view_mode(old_mode)
        else:
            # self.table.reload()
            self.restore()
            self.message(config.str['MSG_BOARD_MODE_%s' % self.mode_thead[self.mode]])

    def finish(self):
        pid = self.table.fetch()['pid']
        if pid is not None:
            self.goto('post', boardname=self.board.boardname, pid=pid)

    #####################

    def goto_line(self):
        no = self.readnum(prompt=u"跳转到哪篇文章？")
        if no is not False:
            self.table.goto(no)
        else:
            self.table.restore_cursor_gently()
            self.message(u'放弃输入')

    def change_board(self):
        boardname = self.readline(prompt=u'请输入要切换的版块：')
        board = manager.board.get_board(boardname)
        if board :
            perm = manager.query.get_board_ability(self.session.user.userid, board['boardname'])[0]
            if perm :
                self.goto('board', board=board)
        self.message(u'错误的讨论区或你无权力进入该版')

    def query_user(self):
        self.suspend('query_user_iter')
        
        ####################

    def get_last_pid(self):
        return manager.post.get_last_pid(self.boardname)

    def get_total(self):
        return manager.post.get_board_total(self.boardname)

    def goto_last(self):
        self.table.goto(self.get_total() -1)

    input_mode_map = {
        "1":1, "2":2, "3":3, "0":0,
        }
    def change_mode(self):
        s = self.readline(prompt=u'0)一般模式 1) 文摘 2)被m文章 3)同主题折叠 ', acceptable=ac.isdigit)
        if s in self.input_mode_map :
            self.set_view_mode(self.input_mode_map[s])
        # self.table.goto(0)  #!!!  Ugly but work.
        # self.restore()

    def set_g_mode(self):
        self.set_view_mode(1)

    def set_onetopic_mode(self):
        self.set_view_mode(0 if self.mode else 3)

    def goto_bye(self):
        self.goto('finish')
        
    ###############
    # Edit/Reply  #
    ###############

    def new_post(self):
        self.suspend('new_post', board=self.board)

    def reply_to_author(self):
        p = self.table.fetch()
        self.suspend('send_mail', touserid=p['owner'])

    def set_replyable(self):
        p = self.table.fetch()
        if p.owner == self.userid :   ######### check perm
            p['replyable'] = not p['replyable']
            manager.admin.set_post_replyattr(self.userid, self.boardname,
                                             p.pid, p.replyable)
            self.table.set_hover_data(p)            

    def edit_post(self):
        p = self.table.fetch()
        self.suspend('edit_post', board=self.board, post=p)

    def edit_title(self):
        p = self.table.fetch()
        if p.owner == self.userid :  #######  need to check perm
            title = self.readline(prompt=u'新标题：',prefix=p['title'])
            if not title:
                self.message(u'放弃操作')
                return
            p['title'] = title
            manager.action.update_title(self.userid,self.boardname,
                                        p['pid'], title)
            self.table.set_hover_data(p)
        else:
            self.message(u'你没有该权限！')

    def del_post(self):
        p = self.table.fetch()
        if p['owner'] == self.userid :
            if self.readline(buf_size=1,prompt=u"删除你的文章?[y/n] ") in ac.ks_yes : 
                manager.admin.remove_post_personal(self.userid, self.boardname, p['pid'])
                self.restore()
                self.message(u'自删成功')
        elif self.perm[3] :
            if self.readline(buf_size=1,prompt=u'将文章放入废纸篓？[y/n] ') in ac.ks_yes :
                manager.admin.remove_post_junk(self.userid, self.boardname, p['pid'])
                self.restore()
                self.message(u'删贴成功')

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
                    self.restore()
                else:
                    self.message(u'错误的输入')
            else:
                self.message(u'错误的输入')

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
        if hasattr(self, 'mode') and self.mode != 0 :
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

    def check_admin_perm(self):
        pass

    def set_g_mark(self):
        p = self.table.fetch()
        p = manager.admin.set_g_mark(self.userid, self.board, p)
        self.table.set_hover_data(p)

    def set_m_mark(self):
        p = self.table.fetch()
        p = manager.admin.set_m_mark(self.userid, self.board, p)
        self.table.set_hover_data(p)

    def query_author(self):
        userid = self.table.fetch()['owner']
        self.suspend('query_user', userid=userid)        

    def show_help(self):
        self.suspend('help', page='board')

    def set_deny(self):
        if manager.query.get_board_ability(self.session.user.userid, self.boardname)[3] :
            self.suspend('sys_set_board_deny', boardname=self.boardname)

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
