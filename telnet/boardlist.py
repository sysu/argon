# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import mark
from chaofeng.ui import SimpleTable,HiddenInput,AppendTable
from model import manager
from argo_frame import ArgoFrame
from libtelnet import zh_format_d

import config

class ArgoTableFrame(ArgoFrame):

    def setup(self, table, help_text, thread, data, fformat):
        self.thread = thread
        self.input = self.load(HiddenInput, text=help_text, start_line=2)
        self.table = self.load(table, start_line=4)
        self.table.reset(data, fformat)
        self.restore()

    def restore(self):
        self.cls()
        self.top_bar()
        self.writeln(ac.move2(2,0)+self.input.text)
        self.writeln(self.thread)
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
        self.boards = data
        self.max_index = len(data)
        super(ArgoBoardListTableFrame, self).setup(SimpleTable,
                                                   config.str['BOARDLIST_QUICK_HELP'],
                                                   config.str['BOARDLIST_THEAD'],
                                                   data, self.fformat)

    def fformat(self, li):
        return self.render_str('boardlist-li', **li)

    def get(self, data):
        super(ArgoBoardListTableFrame,self).get(data)
        self.try_action(config.hotkeys['boardlist'].get(data))
        self.try_action(config.hotkeys['boardlist_table'].get(data))

    def go_first(self):
        self.table.goto_first()

    def go_last(self):
        self.table.goto(self.max_index)

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

    def change_sort(self):
        self.mode += 1
        if self.mode > 3 :
            self.mode = 0
        self.data.setup(mode=self.mode)
        self.refresh()

@mark('boardlist')
class ArgoBoardListFrame(ArgoBoardListTableFrame):
    
    def initialize(self,sid=None):
        super(ArgoBoardListFrame, self).initialize()
        if sid is None:
            data = manager.board.get_all_books()
        else:
            data = manager.board.get_by_sid(sid)
        self.setup(data)

    @property
    def status(self):
        return dict(sid=self.sid)

    @classmethod
    def describe(cls,s):
        return u'讨论区列表          -- 分类 %s' % s['sid']
  
    def finish(self):
        r = self.table.fetch()
        if r :
            self.suspend('board',boardname=r['boardname'])

    def show_help(self):
        self.suspend('help',page='boardlist')


