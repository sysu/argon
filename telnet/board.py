# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
    
from chaofeng import Frame,EndInterrupt,Timeout
from chaofeng.g import mark,static
from chaofeng.ui import TextInput,Password,Animation,ColMenu,Table
from datetime import datetime
import config
import chaofeng.ascii as ac

'''
实现讨论区相关的Frame。

'''

class BoardListTable(Table):

    kmap = Table.kmap
    
    kmap['k'] = Table.move_up
    kmap['j'] = Table.move_down
    kmap['p'] = Table.page_up
    kmap[ac.k_ctrl_p('b')] = Table.page_up
    kmap['b'] = Table.page_up
    kmap['n'] = Table.page_down
    kmap[ac.k_ctrl_p('f')] = Table.page_down
    kmap[' '] = Table.page_down

    def __init__(self,frame,line=0):
        Table.__init__(self,frame,"%s",line=line,data=[0,1,2,3,4],limit=3)
        self.buf = []

    def send(self,data):
        Table.send(self,data)
        if data.isdigit() :
            self.buf.append(data)

@mark('boardlist')
class BoardListFrame(Frame):
    '''
    实现讨论区列表。

    @para sid : 分类编号为sid的讨论区
    @para new : 有新文章发布的讨论区
    '''
    background = static['boardlist'].safe_substitute(
        pos="%(pos)8s",
        pos_info="%(pos_info)10s",
        content="%(content)s",
        time="%(time)24s",
        online="%(online)4d",
        online_friend="%(online_friend)4d",
        username="%(username)10s")
    
    def initialize(self,sid=0,new=None):
        self.table = BoardListTable(self)

    def get(self,data):
        # for c in data :
        #     print ord(c),
        # print
        self.table.send(data)

