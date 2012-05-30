# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import static,mark
from chaofeng.ui import SimpleTable,HiddenInput
from model import manager
from argo_frame import ArgoStatusFrame,in_history

import config

class PostMapper:

    format_str = static['board'][2]
    
    def __init__(self):
        pass

    def setup(self):
        pass
    
    def __getitem__(self,key):
        return self.format_str % dict(read=u'◆',
                                      online=manager.online.board_online(self._data[key]['boardname']) or 0,
                                      mark='',
                                      **self._data[key])

    def raw(self):
        return self._data

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
            ac.k_right:"finish",
            "q":"go_back",
            "e":"go_back",
            ac.k_left:"goto_back",
            "s":"change_sort",
            "S":"send_message",
            "f":"goto_friend",
            "!":"goto_out",
            ac.k_ctrl_z:"watch_message",
            "h":"show_help",
            "H":"goto_top_ten",
            "u":"goto_check_user",
            "l":"goto_mail",
            ac.k_ctrl_a:"watch_board",
            "X":"set_readonly",
            ac.k_ctrl_e:"change_board_attr",
            })            
            
    thread = static['boardlist'][2]
    x_table = SimpleTable(start_line=4)
    x_input = HiddenInput(text=static['boardlist'][0],start_line=2)

    help_page = 'sections'
        
    def initialize(self,sid=None,default=0,sort=0):
        self.data = BoardMapper()
        self.table = self.load(self.x_table,self.data,refresh=False)
        self.input = self.load(self.x_input)
        self.sort = sort
        self.sid = sid
        self.set_data(sid=sid)
        self.refresh()
        
    def refresh(self):
        self.cls()
        self.top_bar()
        self.writeln(self.input.text)
        self.writeln(self.thread)
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
        text = self.input.read(prompt=u"跳转到哪个讨论区？")
        self.table.refresh_cursor()
        try:
            g = int(text)
        except:
            return
        self.table.goto(g)

    def goto_with_prefix(self,data):
        for index,item in enumerate(self.data.raw()) :
            if item['boardname'].startswith(data):
                self.write(ac.save)
                self.table.goto(index)
                self.write(ac.restore)
                return
            
    def search(self):
        text = self.input.read_with_hook(hook = lambda x : self.goto_with_prefix(x) ,
                                         prompt=u'搜寻讨论区：')
        self.table.refresh_cursor()
        
    def change_sort(self):
        self.sort += 1
        if self.sort > 3 :
            self.sort = 0
        self.data.setup(sort=self.sort)
        self.refresh()

    def hover_now(self):
        return self.data.raw()[self.table.fetch()]

    def watch_board(self):
        self.goto('board_info',self.hover_now()['boardname'])

    def set_readonly(self):
        pass

    def change_board_attr(self):
        pass

    @in_history
    def finish(self):
        print self.table.fetch()
