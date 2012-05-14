# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

# from chaofeng import EndInterrupt,Timeout
# from chaofeng import mark,static
# from chaofeng.ui import ColMenu
# import chaofeng.ascii as ac

from chaofeng import static
from chaofeng.g import mark
from chaofeng.ui import BaseTable,SingleTextBox,TextEditor,LongTextBox
from chaofeng import ascii as ac
from model import *
from datetime import datetime
from argo_frame import ArgoBaseFrame,ArgoStatusFrame,\
    ArgoKeymapsFrame,in_history,ex_curses
import chaofeng.ascii as ac
from argo_editor import ArgoEditor
import config
import re

class BaseTableFrame(ArgoStatusFrame):

    key_maps = {
        ac.k_up : "move_up",
        ac.k_down : "move_down",
        ac.k_page_down : "page_down",
        ac.k_page_up : "page_up",
        ac.k_home : "go_first",
        ac.k_end : "go_last",
        ac.k_ctrl_c : "goto_back",
        "h":"show_help",
        "q":"goto_back",
        ac.k_left:"goto_back",
        ac.k_right:"finish",
        }

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

    def finish(self):
        raise NotImplementedError

    def go_last(self):
        self.table.goto(len(self.table.data))

@mark('boardlist')
class BoardListFrame(BaseTableFrame):

    key_maps = BaseTableFrame.key_maps.copy()
    
    x_table = BaseTable(start_line=4)
    
    help_info = static['boardlist'][0] + '\r\n'
    thead = tuple(static['boardlist'][1:3])
    format_strs = tuple(static['boardlist'][3:5])
    
    class Wrapper:

        def __init__(self,data):
            self.data = data
            self.len = len(data)
                        
        def __getitem__(self,key):
            board = self.data[key]
            return {
                "total":board.get_total(),
                "boardname":board['boardname'],
                "description":board['description'],
                'online':board.count_online(),
                'bm': board['bm'] and ' '.join(board['bm'].split(':')),
                }
        
        def __len__(self):
            return self.len

    def initialize(self,section_name='Test',mode=0,default=0):
        self.mode = mode
        self.section_name = section_name
        self.data = self.Wrapper(db_orm.get_boards(section_name))
        self.table = self.load(self.x_table,
                               self.format_strs[mode],
                               self.data,default=default,refresh=False)
        self.refresh()

    def refresh(self):
        self.cls()
        self.top_bar(left=u'[讨论区列表]')
        self.write(self.help_info)
        self.write(self.thead[self.mode])
        self.bottom_bar(repos=True)
        self.table.refresh()

    def record_x(self):
        self.record(section_name=self.section_name,
                    mode=self.mode,default=self.table.hover)

    @in_history
    def show_help(self):
        self.goto('tutorial','tut_boardlist')

    @in_history
    def finish(self):
        d = self.table.fetch()
        self.goto('board',self.data[d]['boardname'])
        
@mark('board')
class BoardFrame(BaseTableFrame):

    key_maps = BaseTableFrame.key_maps.copy()
    key_maps.update({
            ac.k_c_p : "new_post",
            })

    x_table = BaseTable(start_line=4)
    help_info = static['board'][0] + '\r\n'
    thread = static['board'][1]
    format_str = static['board'][2]

    class Wrapper:

        def __init__(self,boardobj):
            self.board = boardobj
            self.start = -20  # Max Row
            self.limit = 20
            self.res = []
            self.len = int(boardobj.get_total())

        def get_post(self,key):
            if key >= self.len : return None
            pos = key - self.start
            if pos >= self.limit or pos < 0 :
                pos = key % self.limit
                self.start = key - pos
                self.len = int(self.board.get_total())
                self.res = self.board.get_post(self.start,
                                               self.start + self.limit)
            return self.res[pos]

        def __getitem__(self,key):
            d = self.get_post(key).dict.copy()
            d['number'] = key
            d['data'] = d['posttime'].strftime("%b %d %a")
            return d

        def __len__(self):
            return self.len
            
    def initialize(self,boardname,default=0):
        self.session.lastboard = boardname
        self.boardname = boardname
        self.session.last_board = boardname
        self.data = db_orm.get_board(boardname)
        self.w_data = self.Wrapper(self.data)
        self.table = self.load(self.x_table,
                               self.format_str,
                               self.w_data,default=default,refresh=False)
        self.refresh()

    def refresh(self):
        self.cls()
        self.top_bar(left=self.data['bm'],mid=self.boardname)
        self.write(self.help_info)
        self.write(self.thread)
        self.bottom_bar(repos=True)
        self.table.refresh()

    def record_x(self):
        self.record(boardname=self.boardname,
                    default=self.table.hover)

    @in_history
    def finish(self):
        self.goto('post',self.w_data.get_post(self.table.fetch()))

    @in_history
    def show_help(self):
        self.goto('tutorial','tut_board')

    @in_history
    def new_post(self):
        self.goto('add_post',self.boardname)

    # def finish(self):
    #     self.record(section_name=self.section_name,
    #                 mode=self.mode,default=self.table.hover)

    # @in_history
    # def new_post(self):
    #     d = self.table.fetch()
    #     self.goto('post',self.boardname,
        

@mark('post')
class PostFrame(ArgoBaseFrame):

    class ArgoTextBox(LongTextBox):

        def handle_finish(self):
            self.frame.goto_back()

    x_cbox = ArgoTextBox()

    def initialize(self,postobj):
        self.body = postobj
        self.post = self.load(self.x_cbox,postobj['content'])
        
    def get(self,data):
        self.post.send(data)

@mark('add_post')
class AddPostFrame(ArgoBaseFrame):

    re_c = re.compile('[^\r\n]+')
    x_editor = ArgoEditor()
    key_maps = {
        ac.k_ctrl_c : "cancel",
        }
    
    def initialize(self,boardname):
        self.write(ac.clear)
        self.boardname = boardname
        self.editor = self.load(self.x_editor)
        self.editor.refresh()

    def get(self,data):
        self.editor.send(data)
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()

    @ex_curses
    def cancel(self):
        self.editor.message(u'按下y确认发布，Ctrl+C离开')
        c = self.read_secret()
        if c == 'y' :
            content = self.editor.fetch()
            title_re = re.match(self.re_c,content)
            if not title_re  :
                self.write(u'错误的标题！')
                return
            title = title_re.group(0),
            p = {
                'title':title,
                'content':content,
                }
            self.session._user.add_post(self.boardname,p)
            self.editor.message(u'发帖成功！ 《%s》' % title)
            self.goto_back()
        elif c == ac.k_ctrl_c :
            self.goto_back()
        
# todo :
# better wrap up for UI,Frame, and Frame,get
