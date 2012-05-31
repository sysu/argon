# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import static,mark
from chaofeng.ui import SimpleTable,HiddenInput
from model import manager
from argo_frame import ArgoStatusFrame,in_history

import config

# 1 文摘
# 2 同主题
# 3 美文
# 4 原作
# 5 同作者
# 6 标题关键字

class PostWrapper:

    def __init__(self,boardname,total,limit=20,start=-20,mode=0):
        self.total = total
        self.limit = limit
        self.start = start
        self.boardname = boardname
        self.setup(mode)

    def setup(self,mode):
        if mode == 0:
            self.select = lambda offset,limit : manager.\
                post.get_posts_by_boardname(self.boardname,offset,limit)
        elif mode == 1:
            self.select = lambda offset,limit : manager.\
                post.get_g_posts_by_boardname(self.boardname,offset,limit)                
        elif mode == 2:
            self.select = lambda offset,limit : manager.\
                post.get_posts_by_boardname(self.boardname,offset,limit,order='tid')
        elif mode == 3:
            self.select = lambda offset,limit : manager.\
                post.get_m_posts_by_boardname(self.boardname,offset,limit)
        elif mode == 4:
            self.select = lambda offset,limit : manager.\
                post.get_topic_by_boardname(self.boardname,offset,limit)
        # todo:
        #    mode 5,and mode 6

    def format(self,d):
        return "%5s  %12s %6 %ss" % (d['pid'],d['owner'],
                                     d['posttime'].strftime("%b %d %a"),
                                     d['title'])

    def get(self,limit,offset):
        return map(self.format,self.select(limit,offset))

    def __len__(self):
        return self.total

@mark('board')
class BaseTableFrame(ArgoStatusFrame):

    key_maps = config.TABLE_KEY_MAPS.copy()
    key_maps.update({
            })            
            
    thread = ["TableHead"]
    x_table = SimpleTable(start_line=4)
    x_input = HiddenInput(text="help info",start_line=2)

    help_page = 'board'
        
    def initialize(self,boardname=None,default=0,mode=0):
        self.mode = mode
        self.data = PostWrapper(boardname,manager.post.get_board_total(boardname))
        self.table = self.load(self.x_table,self.data,refresh=False)
        self.input = self.load(self.x_input)
        self.boardname = boardname
        self.set_mode(mode)
        self.refresh()
        
    def refresh(self):
        self.cls()
        self.top_bar()
        self.writeln(self.input.text)
        self.writeln(self.thread[self.mode])
        self.bottom_bar(repos=True)
        self.table.refresh()

    def set_mode(self,mode):
        self.data.setup(mode)

    def handle_record(self):
        self.record(boardname=self.boardname,default=self.table.hover,mode=mode)
        
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
        text = self.input.read(prompt=u"跳转到哪号文章？")
        self.table.refresh_cursor()
        try:
            g = int(text)
        except:
            return
        self.table.goto(g)

    # def goto_with_prefix(self,data):
    #     for index,item in enumerate(self.data.raw()) :
    #         if item['boardname'].startswith(data):
    #             self.write(ac.save)
    #             self.table.goto(index)
    #             self.write(ac.restore)
    #             return
            
    # def search(self):
    #     text = self.input.read_with_hook(hook = lambda x : self.goto_with_prefix(x) ,
    #                                      prompt=u'搜寻讨论区：')
    #     self.table.refresh_cursor()

    def try_jump_board(self):
        pass

    def watch_owner(self):
        pass

    def clear_unread(self):
        pass

    def set_1_mode(self):
        self.set_mode(1)

    def set_4_mode(self):
        self.set_mode(2)

    def select_mode(self):
        pass

    def watch_note(self):
        pass

    def watch_secret_note(self):
        pass

    def lock_screen(self):
        pass

    def jump_essence(self):
        pass

    def clear_all_unread(self):
        pass

    def set_noreply(self):
        pass

    def jump_same_topic(self):
        pass

    def jump_same_owner(self):
        pass

    def jump_new_first(self):
        pass

    def jump_topic_first(self):
        pass

    def jump_topic_last(self):
        pass

    def jump_select(self):
        pass

    def change_mode(self):
        pass

    def find_author(self):
        pass

    def find_title(self):
        pass

    def goto_board(self):
        pass

    def find_content(self):
        pass

    def new_post(self):
        pass

    def edit_post(self):
        pass

    def edit_title(self):
        pass
    
    def delet_post(self):
        pass

    def repost(self):
        pass

    def reply_author(self):
        pass

    def save_to_mail(self):
        pass

    # def
    # 暂存区???

    def set_post_g(self):
        pass

    def set_post_m(self):
        pass

    def push_to_ess(self):
        pass

    # 设置版面档案、设置备忘录密码、

    def delete_posts_r(self):
        pass

    def not_post_sb(self):
        pass

    def goto_trash(self):
        pass

    def restore_posts_r(self):
        pass

    def restore_post(self):
        pass

    def hover_post(self):
        pass

    def push_hove_to_ess(self):
        pass

    def work_same_topic(self):
        pass

    def recommend(self):
        pass

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
