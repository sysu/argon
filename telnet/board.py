# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import static,mark
from chaofeng.ui import SimpleTable,HiddenInput
from model import manager
from argo_frame import ArgoFrame

import config

# 1 文摘
# 2 同主题
# 3 美文
# 4 原作
# 5 同作者
# 6 标题关键字

class ArgoBoardTable(ArgoFrame):

    key_maps = ArgoFrame.key_maps.copy()
    key_maps.update({
            ###############
            # move cursor #
            ###############
            # move_up,move_down,go_first,page_up,page_down,go_first,go_last,
            # go_line, !!! go_topic_first, go_topic_last,
            "k":"move_up",ac.k_up:"move_up",
            "j":"move_down",ac.k_down:"move_down",
            "P":"page_up","N":"page_down",
            ac.k_home:"go_first",ac.k_end:"go_last","$":"go_last","#":"go_line",

            ###############
            # Read/common #
            ###############
            # !!! read,clearall_unread,goto_digest,read_same_topic,read_same_author,
            # read_topic_unread_first,remove_unread, goto_note, goto_snote
            # goto_userpage, goto_topten
            ac.k_right:"read",

            ###############
            # Edit/Reply  #
            ###############
            ac.k_ctrl_p:"new_post",
            # new_post,edit_post,edit_title,del_post,reproduced, !!!send_mail_author,
            # send_mail_self

            ###############
            # Search/Mode #
            ###############
            # goto_board, vote??, hidden??, search_author, search_title
            # search_content, g_mode, y_mode, select_mode, change_mode

            ###############
            # Jump        #
            ###############
            "h":"show_help",ac.k_left:"goto_back",
            # pass

            ###############
            # admin       #
            ###############
            # not_post, deal_author, vote??, set_readonley, goto_postinfo,
            # set_snote_passwd, del_post[before], del_post_range,
            # deal_topic, restore_post, restore_post_range, goto_trash
            # save_temp??, set_g, set_m, push_digest,
            # mark_this, put_mark_digest, 废纸篓？清空回收站？

            })

    _input = HiddenInput(text=static['board'][0],start_line=2)
    _table = SimpleTable(start_line=4)
    thread = static['board'][1]

    def initialize(self,default=0,display=True):
        self.input_ = self.load(self._input)
        self.table_ = self.load(self._table,default=default)
        self.bind(self.get_getdata(),self.get_fformat())
        if display:
            self.display()
        
    def display(self):
        self.cls()
        self.top_bar()
        self.writeln(self.input_.text)
        self.writeln(self.thread)
        self.bottom_bar(repos=True)
        self.table_.refresh()

    def bind(self,getdata,fformat):
        self.table_.setup(getdata=getdata,fformat=fformat,refresh=False)

    def get(self,data):
        if data in ac.ks_finish:
            self.finish()
        self.try_action(data)

    def get_getdata(self):
        raise NotImplementedError

    def get_fformat(self):
        raise NotImplementedError

    def get_last_index(self):
        raise NotImplementedError

@mark('board')
class ArgoBoardFrame(ArgoBoardTable):

    help_page = 'board'
        
    def initialize(self,boardname=None,default=0,mode=0):
        self.set_mode(mode,refresh=False)
        self.boardname = boardname
        super(ArgoBoardFrame,self).initialize(default)

    @property
    def status(self):
        return dict(boardname=self.boardname,
                    default=self.table_.hover,
                    mode=self.mode)

    @classmethod
    def describe(self,s):
        return u'讨论区[%s]' % s['boardname']

    def get_getdata(self):
        return lambda o,l: manager.post.get_posts_advan(self.boardname,o,l)

    def get_fformat(self):
        return lambda d : "%5s  %12s %6s %s" % (d['pid'],d['owner'],
                                                d['posttime'].strftime("%b %d %a"),
                                                d['title'])

    def get_last_index(self):
        return manager.post.get_last_pid(self.boardname)

    def set_mode(self,mode,refresh=True):
        self.mode = mode
        if refresh:
            self.display()

    ###############
    # move cursor #
    ###############

    def move_up(self):
        self.table_.move_up()

    def move_down(self):
        self.table_.goto_offset(1)
        
    def page_up(self):
        self.table_.goto_offset(-self.table_.limit)
    
    def page_down(self):
        self.table_.goto_offset(self.table_.limit)

    def go_first(self):
        self.table_.goto(0)

    def go_last(self):
        self.table_.goto(self.get_last_index())

    def go_line(self):
        text = self.input_.read(prompt=u"跳转到哪篇文章？")
        self.table_.refresh_cursor()
        try:
            g = int(text)
        except:
            return
        self.table_.goto(g)

    ###############
    # Read/common #
    ###############

    ###############
    # Edit/Reply  #
    ###############

    def new_post(self):
        self.suspend('new_post',boardname=self.boardname)

    def edit_post(self):
        self.suspend('edit_post',boardname=boardname,pid=self.table_.fetch()['pid'])

    def edit_title(self):
        text = self.input_.read(prompt=u'新标题：')
        self.table_.refresh_cursor()
        manager.action.update_title(self.userid,self.boardname,
                                    self.table_.fetch()['pid'], text)

    def del_post(self):
        pass

    def reproduced(self):
        pass

    def finish(self):
        self.suspend('post',
                     boardname=self.boardname,
                     pid=self.table_.fetch()['pid'])
        
    def show_help(self):
        self.suspend('help',page='board')
