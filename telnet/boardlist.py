# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import static,mark
from chaofeng.ui import SimpleTable,HiddenInput
from model import manager
from argo_frame import ArgoFrame

import config

static['boardlist'][4] = u'%(total)5s%(read)3s %(boardname)-18s [%(tp)4s]    %(description)-20s%(online)4s %(mark)2s %(bm)-13s'
static['boardlist'][2] = u'[1;44m 全部  未 讨论区名称          类别  转 中  文  叙  述       在线 S 版  主       '

class ArgoBoardListTable(ArgoFrame):

    key_maps = ArgoFrame.key_maps.copy()
    key_maps.update({
        # cursor
        ac.k_up:"move_up",      'k':'move_up',
        ac.k_down:"move_down",  'j':'move_down',
        'P':'page_up',          ac.k_ctrl_b:'page_up',        'b':'page_up',
        'N':'page_down',        ac.k_ctrl_f:'page_down',      ' ':'page_down',
        ac.k_home:'go_first',   ac.k_end:"go_last",           '$':'go_last',
        '#':'go_line',

        # mode/serach
        '/':'search',         ac.k_right:'finish',
        'q':'goto_back',      'e':'goto_back',        ac.k_left:'goto_back',
        's':'change_sort',

        # jump
        'S':'send_message',     ac.k_ctrl_z:'watch_message',
        'f':'goto_friend',      '!':'goto_out',
        'H':'goto_top_ten',     'l':'goto_mail',
        'h':'help',        'u':'goto_check_user',

        # admin
        ac.k_ctrl_a:'watch_board',
        'X':'set_readonly',
        ac.k_ctrl_e:'change_board_attr',
        })

    _input = HiddenInput(text=static['boardlist'][0],start_line=2)
    _table = SimpleTable(start_line=4)
    thread = static['boardlist'][2]
    
    def initialize(self,default=0,mode=None,display=True):
        self.input_ = self.load(self._input)
        self.table_ = self.load(self._table,default=default)
        self.bind(self.get_getdata(),self.fformat)
        self.mode = 0
        if mode is not None:
            self.sort(mode)
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

    def get_last_index(self):
        raise NotImplementedError

    ##################
    # Move cursor    #
    ##################
        
    def move_up(self):
        self.table_.goto_offset(-1)

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
        text = self.input_.read(prompt=u"跳转到哪个讨论区？")
        self.table_.refresh_cursor()
        try:
            g = int(text)
        except:
            return
        self.table_.goto(g)

    #################
    # search/sort   #
    #################

    def goto_with_prefix(self,data):
        for index,item in enumerate(self.data.raw()) :
            if item['boardname'].startswith(data):
                self.write(ac.save)
                self.table.goto(index)
                self.write(ac.restore)
                return
            
    def search(self):
        text = self.input_.read_with_hook(hook = lambda x : self.goto_with_prefix(x) ,
                                         prompt=u'搜寻讨论区：')
        self.table.refresh_cursor()

    def sort(self,mode):
        if mode == 1 :
            self.table_.data.sort(key = lambda x: \
                                manager.online.board_online(x['boardname'] or 0),
                            reverse=True)
        elif mode == 2:
            self.table_.data.sort(key = lambda x: x['boardname'])
        elif mode == 3:
            self.table_.data.sort(key = lambda x: x['description'])

    def change_sort(self):
        self.mode += 1
        if self.mode > 3 :
            self.mode = 0
        self.data.setup(mode=self.mode)
        self.refresh()

    ###########
    # Jump    #
    ###########

    # todo

    ###########
    # admin   #
    ###########

    # todo

@mark('boardlist')
class BoardListFrame(ArgoBoardListTable):
    
    help_page = 'boardlist'
    format_str = static['boardlist'][4]

    def initialize(self,sid=None,default=0,mode=None):
        self.sid = sid
        super(BoardListFrame,self).initialize(default=default,mode=mode)

    def fformat(self,x):
        return self.format_str % dict(read=u'◆',
                                      online=manager.online.board_online(x['boardname']) \
                                          or 0,
                                      mark='',
                                      **x)
        
    def get_getdata(self):
        if self.sid is None:
            self.boards = manager.board.get_all_boards()
        else:
            self.boards = manager.board.get_by_sid(self.sid)
        return lambda l,f: self.boards[l:l+f]

    def get_last_index(self):
        return len(self.boards)

    @property
    def status(self):
        return dict(sid=self.sid,default=self.table_.hover,mode=self.mode)
  
    def finish(self):
        r = self.table_.fetch()
        self.suspend('board',boardname=r['boardname'])
