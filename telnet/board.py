# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

__metaclass__ = type

from chaofeng import ascii as ac
from chaofeng.g import static,mark
from chaofeng.ui import HiddenInput,ModeAppendTable
from model import manager
from argo_frame import ArgoFrame
from libtelnet import zh_format

import config

# 1 文摘
# 2 同主题
# 3 美文
# 4 原作
# 5 同作者
# 6 标题关键字

class ArgoBoardTable(ArgoFrame):

    _input = HiddenInput(text=static['board'][0],start_line=2)
    _table = ModeAppendTable('pid', start_line=4)
    thead = static['board'][1]

    def initialize(self,boardname=None,default=0,mode=0):
        manager.action.enter_board(self.userid,self.seid,boardname)
        self.lastboard = boardname
        self.set_mode(mode,refresh=False)
        self.boardname = boardname
        self.set_up(((lambda s,l : manager.post.get_posts(self.boardname,s,l),
                    self.get_fformat())), default)
        
    def set_up(self, get_posts, format_posts, default=0,display=True):
        self.input_ = self.load(self._input)
        self.table_ = self.load(self._table, get_posts, format_posts)
        self.table_.set_mode(0)
        self.table_.load_with_upper(self.get_last_index())
        if display:
            self.restore()
        # (lambda s,l : manager.post.get_posts(self.boardname,s,l),
        # self.get_fformat())

    def restore(self):
        self.cls()
        self.top_bar()
        self.writeln(self.input_.text)
        self.writeln(self.thead)
        self.bottom_bar()
        self.table_.restore()

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
            ac.k_right:"finish",

            ###############
            # Edit/Reply  #
            ###############
            ac.k_ctrl_p:"new_post",ac.k_ctrl_r:"reply_post","E":"edit_post",
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
    
    def clear(self):
        manager.action.exit_board(self.userid,self.seid,self.boardname)

    @property
    def status(self):
        return dict(boardname=self.boardname,
                    default=self.table_.hover,
                    mode=self.mode)

    @classmethod
    def describe(self,s):
        return u'讨论区              -- %s' % s['boardname']

    def get_getdata(self):
        return lambda o,l: manager.post.get_posts_advan(self.boardname,o,l)

    def get_fformat(self):
        return lambda d : self.fm("%5s   %-12s %-10s %s",
                                  (d['pid'],d['owner'],
                                   d['posttime'].strftime("%b %d"),
                                   d['title']))

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
        self.table_.move_down()
        
    def page_up(self):
        self.table_.goto_offset(-self.table_.limit)
    
    def page_down(self):
        self.table_.goto_offset(self.table_.limit)

    def go_first(self):
        self.table_.goto(0)
