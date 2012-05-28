# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import static,mark
from chaofeng.ui import SimpleTable
from model import manager
from argo_frame import ArgoStatusFrame,in_history

import config

static['boardlist'][4] = u'%(total)5s%(read)3s %(boardname)-18s [%(tp)4s]    %(description)-20s%(online)4s %(mark)2s %(bm)-13s'
static['boardlist'][2] = u'[1;44m 全部  未 讨论区名称          类别  转 中  文  叙  述       在线 S 版  主       '

class BoardMapper:

    format_str = static['boardlist'][4]
    
    def __init__(self,sid=None):
        self.setup(sid)
        
    def setup(self,sid=None):
        if sid :
            print sid
            lmd = lambda : manager.board.get_by_sid(sid)
            self.select = lmd
            self._data = self.select()

    def __getitem__(self,key):
        return self.format_str % dict(read=u'◆',
                                      online=manager.online.board_online(self._data[key]['boardname']) or 0,
                                      mark='',
                                      **self._data[key])

    def __len__(self):
        return len(self._data)

@mark('boardlist')
class BaseTableFrame(ArgoStatusFrame):

    key_maps = config.TABLE_KEY_MAPS.copy()
    key_maps.update({
            "k":"move_up",
            "j":"move_down",
            "P":"page_up",
            ac.k_ctrl_b:"page_up",
            'b':"page_up",
            "N":"page_down",
            ac.k_ctrl_f:"page_down",
            " ":"page_down",
            "#":"try_jump",
            "$":"go_last",
            "/":"search",
            ac.k_right:"finish"
            "q":"go_back",
            "e":"go_back",
            ac.k_left:"go_back",
            "s":"change_sort",
            "S":"send_message",
            "f":"goto_friend",
            "!":"goto_out",
            ac.k_ctrl_z:"watch_message",
            "H":"goto_top_ten",
            "u":"goto_check_user",
            "l":"goto_mail",
            ac.k_ctrl_a:"watch_board",
            "X":"set_readonly",
            ac.k_ctrl_e:"change_board_attr",
            })            
            
    help_info = static['boardlist'][0]
    thread = static['boardlist'][2]
    x_table = SimpleTable(start_line=4)
    
    def initialize(self,sid=None,default=0):
        self.data = BoardMapper()
        self.table = self.load(self.x_table,self.data,refresh=False)
        self.set_data(sid=sid)
        self.refresh()
        
    def refresh(self):
        self.cls()
        self.top_bar()
        self.writeln(self.help_info)
        self.write(self.thread)
        self.bottom_bar(repos=True)
        self.table.refresh()

    def set_data(self,sid):
        self.data.setup(sid)

    def handle_record(self):
        self.record(sid=self.sid,default=self.table.hover)
        
    def get(self,data):
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()
        if data in ac.ks_finish :
            self.finish()
  
    def move_down(self):
        self.table.goto_offset(1)
    
    def move_up(self):
        self.table.goto_offset(-1)

    def page_down(self):
        self.table.goto_offset(self.table.limit)
        
    def page_up(self):
        self.table.goto_offset(-self.table.limit)

    def go_first(self):
        self.table.goto(0)

    def go_last(self):
        self.table.goto(len(self.table.data))

#todo:2012-5-29-01:58

    def try_jump(self):
        pass

    def search(self):
        pass

    def change_sort(self):
        pass

    def watch_board(self):
        pass

    def set_readonly(self):
        pass

    def change_board_attr(self):
        pass

    @in_history
    def finish(self):
        print self.table.fetch()
