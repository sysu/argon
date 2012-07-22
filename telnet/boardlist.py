# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import mark
from chaofeng.ui import PagedTable#,HiddenInput#,AppendTable#SimpleTable,
from model import manager
from argo_frame import ArgoFrame
from libtelnet import zh_format_d
from view import ArgoTextBoxFrame
import config

class ArgoTableFrame(ArgoFrame):

    def setup(self, table, help_text, thead):
        self.thead = thead
        self.input = self.load(HiddenInput, text=help_text, start_line=2)
        self.table = table

    def reset_thead(self, thead):
        self.thead = thead

    def restore(self):
        self.cls()
        self.top_bar()
        self.writeln(ac.move2(2,0)+self.input.text)
        self.writeln(self.thead)
        self.bottom_bar()
        self.table.restore()

    def get(self, data):
        if data in ac.ks_finish:
            self.finish()
        self.table.try_action(config.hotkeys['table_table'].get(data))
        self.try_action(config.hotkeys['table'].get(data))
        self.try_action(config.hotkeys['g'].get(data))

class ArgoBoardListTableFrame(ArgoTableFrame):

    def setup(self, data):
        self.table = self.load(SimpleTable, start_line=4)
        self.reload_data(data)
        self.mode = 0 # for sort
        super(ArgoBoardListTableFrame, self).setup(self.table,
                                                   config.str['BOARDLIST_QUICK_HELP'],
                                                   config.str['BOARDLIST_THEAD'])

    def reload_data(self, data):
        self.boards = data
        self.max_index = len(data)
        self.table.reset(data, self.fformat)

    def fformat(self, li):
        return self.render_str('boardlist-li', **li)

    def get(self, data):
        super(ArgoBoardListTableFrame,self).get(data)
        self.try_action(config.hotkeys['boardlist'].get(data))
        self.table.try_action(config.hotkeys['boardlist_table'].get(data))
        if data in config.hotkeys['boardlist_jump'] :
            self.goto(config.hotkeys['boardlist_jump'][data])

    def go_last(self):
        print self.max_index
        self.table.goto(self.max_index-1)

    def go_line(self):
        text = self.input.read(prompt=u"跳转到哪个讨论区？")
        self.table.refresh_cursor()
        try:
            g = int(text)
        except:
            return
        for i,d in enumerate(self.boards):
            if d['bid'] == g :
                break
        else:
            return
        self.table.goto(i)

    def goto_with_prefix(self,prefix):
        data = self.table.data
        for index,item in enumerate(data):
            if item['boardname'].startswith(prefix):
                self.write(ac.save)
                self.table.goto(index)
                self.write(ac.restore)
                return
            
    def search(self):
        text = self.input.read_with_hook(hook = lambda x : self.goto_with_prefix(x) ,
                                         prompt=u'搜寻讨论区：')
        self.table.refresh_cursor()

    def sort(self,mode):
        if mode == 1 :
            self.table.data.sort(key = lambda x: \
                                manager.online.board_online(x['boardname'] or 0),
                            reverse=True)
        elif mode == 2:
            self.table.data.sort(key = lambda x: x['boardname'])
        elif mode == 3:
            self.table.data.sort(key = lambda x: x['description'])
        else:
            self.table.data.sort(key = lambda x:x['bid'])

    def change_sort(self):
        self.mode += 1
        if self.mode > 3 :
            self.mode = 0
        self.sort(self.mode)
        self.restore()

    def watch_board(self):
        self.suspend('query_board', bid=self.table.fetch()['bid'])

    def add_to_fav(self):
        manager.favourite.add(self.userid, self.table.fetch()['bid'])
        self.message(u'预定版块成功！')

    def remove_fav(self):
        manager.favourite.remove(self.userid, self.table.fetch()['bid'])
        self.message(u'取消预定版块成功！')

@mark('query_board')
class QueryBoardFrame(ArgoTextBoxFrame):

    def initialize(self, bid):
        super(QueryBoardFrame,self).initialize()
        self.bid = bid
        self.setup()
        self.cls()
        self.set_text(self.query_board(bid))

    def query_board(self, bid):
        board = manager.board.get_board_by_id(bid)
        return self.render_str('board-t',**board)

    def finish(self,a):
        self.goto_back()

    def add_to_fav(self):
        manager.favourite.add(self.userid, self.bid)
        self.message(u'预定版块成功！')

    def get(self, data):
        super(QueryBoardFrame, self).get(data)
        self.try_action(config.hotkeys['view-board'].get(data))

@mark('boardlist')
class ArgoBoardListFrame(ArgoBoardListTableFrame):
    
    def initialize(self,sid=None):
        self.sid = sid
        super(ArgoBoardListFrame, self).initialize()
        if sid is None:
            data = manager.board.get_all_boards()
        else:
            data = manager.board.get_by_sid(sid)
        self.setup(data)
        self.restore()
  
    def finish(self):
        r = self.table.fetch()
        if r :
            self.suspend('board',boardname=r['boardname'])

    def show_help(self):
        self.suspend('help',page='boardlist')

@mark('favourite')
class ArgoFavouriteFrame(ArgoBoardListTableFrame):

    def initialize(self):
        super(ArgoFavouriteFrame, self).initialize()
        self.setup(self.get_data())
        self.restore()

    def get_data(self):
        data = manager.favourite.get_all(self.userid)
        data = map(lambda d : manager.board.get_board_by_id(d),
                   data)
        return data

    def restore(self):
        data = manager.favourite.get_all(self.userid)
        print data
        data = map(lambda d : manager.board.get_board_by_id(d),
                   data)
        self.reload_data(data)
        super(ArgoFavouriteFrame, self).restore()
  
    def finish(self):
        r = self.table.fetch()
        if r :
            self.suspend('board',boardname=r['boardname'])

    def show_help(self):
        self.suspend('help',page='boardlist')

    def add_to_fav(self):
        super(ArgoFavouriteFrame, self).add_to_fav()
        self.reload_data(self.get_data())
        self.table.restore()

    def remove_fav(self):
        super(ArgoFavouriteFrame, self).remove_fav()
        self.reload_data(self.get_data())
        self.table.restore()

class ArgoBoardTableFrame(ArgoTableFrame):

    def setup(self):
        table = self.load(AppendTable, 'pid', start_line=4)
        super(ArgoBoardTableFrame, self).setup(table,
                                               config.str['BOARD_QUICK_HELP'],
                                               config.str['BOARD_THEAD_NORMAL'])

    def reset_table(self, data_loader, fformat):
        self.table.reset_with_upper(data_loader, fformat, None)

    ####################
    # meta
    ####################

    def go_line(self):
        text = self.input.read(prompt=u"跳转到哪篇文章？")
        self.table.refresh_cursor()
        try:
            g = int(text)
        except:
            return
        self.table.goto(g)

@mark('board')
class ArgoBoardFrame(ArgoBoardTableFrame):

    def initialize(self, boardname):
        manager.action.enter_board(self.userid, self.seid, boardname)
        self.session.lastboard = boardname
        self.boardname = boardname
        self.setup()
        self.set_mode(0)
        self.restore()
    
    def clear(self):
        manager.action.exit_board(self.userid,self.seid,self.boardname)

    def set_mode(self, mode):
        if mode == 1:
            thead = config.str['BOARD_THEAD_GMODE']
            get_data = lambda o,l : manager.post.get_posts_g(self.boardname, o, l)
        elif mode == 2:
            thead = config.str['BOARD_THEAD_MMODE']
            get_data = lambda o,l : manager.post.get_posts_m(self.boardname, o, l)
        elif mode == 3:
            thead = config.str['BOARD_THEAD_TOPIC']
            get_data = lambda p,l : manager.post.get_posts_topic(self.boardname, p, l)
        elif mode == 4:
            thead = config.str["BOARD_THEAD_ONETOPIC"]
            get_data = lambda p,l : manager.post.get_posts_onetopic(self.tid,
                                                                    self.boardname,p,l)
        elif mode == 5:
            thead = config.str["BOARD_THEAD_AUTHOR"]
            get_data = lambda p,l : manager.post.get_posts_owner(self.author,
                                                                 self.boardname,p,l)
        else :
            thead = config.str['BOARD_THEAD_NORMAL']
            get_data = lambda o,l : manager.post.get_posts(self.boardname, o, l)
        fformat = self.fformat
        self.mode = mode
        self.reset_thead(thead)
        self.reset_table(get_data, fformat)

    def get(self, data):
        super(ArgoBoardFrame,self).get(data)
        self.try_action(config.hotkeys['board'].get(data))
        self.table.try_action(config.hotkeys['board_table'].get(data))

    def finish(self):
        res = self.table.fetch()
        if res:
            self.suspend('post',
                         boardname=self.boardname,
                         pid=res['pid'])

    def show_help(self):
        self.suspend('help',page='board')

    def fformat(self, d):
        return self.render_str('board-li', **d)

    ###############
    # Read/common #
    ###############
    
    def get_last_pid(self):
        return manager.post.get_last_pid(self.boardname)

    ###############
    # Edit/Reply  #
    ###############

    def new_post(self):
        if manager.perm.has_new_post_perm(self.userid,self.boardname):
            self.suspend('new_post',boardname=self.boardname)

    def reply_post(self):
        pid = self.table.fetch()['pid']
        if manager.perm.has_reply_perm(self.userid,self.boardname,pid):
            self.suspend('reply_post',boardname=self.boardname,replyid=pid)

    def edit_post(self):
        pid = self.table.fetch()['pid']
        if manager.perm.has_edit_perm(self.userid,self.boardname,pid):
            self.suspend('edit_post',boardname=self.boardname,pid=pid)
        else:
            self.message(u'你没有编辑此文章的权限！')

    # def edit_title(self):
    #     text = self.input.read(prompt=u'新标题：')
    #     self.table.refresh_cursor()
    #     manager.action.update_title(self.userid,self.boardname,
    #                                 self.table.fetch()['pid'], text)

    def del_post(self):
        pass

    def reproduced(self):
        pass

    def change_mode(self):
        if self.mode >=3 : mode=0
        else : mode = self.mode+1
        self.set_mode(mode)
        self.restore()

    def hover_pid(self):
        return self.table.fetch()['pid']

    def set_g_mark(self):
        p = self.table.fetch()
        pid = p['pid']
        flag = p['flag'] ^ 1
        manager.post.update_post(self.boardname,pid,flag=flag)
        p['flag'] = flag
        self.table.refresh_hover()

    def set_m_mark(self):
        p = self.table.fetch()
        pid = p['pid']
        flag = p['flag'] ^ 2
        manager.post.update_post(self.boardname,pid,flag=flag)
        p['flag'] = flag
        self.table.refresh_hover()

    def goto_tid(self):
        self.tid = self.table.fetch()['tid']
        self.set_mode(4)
        self.restore()

    def goto_author(self):
        self.author = self.table.fetch()['owner']
        self.set_mode(5)
        self.restore()

    def goto_back(self):
        if self.mode != 0 :
            self.set_mode(0)
            self.restore()
            return
        super(ArgoBoardFrame, self).goto_back()

    def clear_readmark(self):
        last = self.get_last_pid()
        manager.readmark.clear_unread(self.userid, self.boardname, last)
        self.restore()

    def set_read(self):
        pid = self.hover_pid()
        manager.readmark.set_read(self.userid, self.boardname, pid)
        self.table.refresh_hover()

    def query_author(self):
        userid = self.table.fetch()['owner']
        self.suspend('query_user', userid=userid)
        
