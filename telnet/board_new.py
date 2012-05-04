# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import Frame,static,EndInterrupt
from chaofeng.g import mark
from chaofeng.ui import Table,TextBox,TextEditor
from chaofeng import ascii as ac
from libtelnet import TBoard,str_top,str_bottom
from model import *
from datetime import datetime

@mark('boardlist')
class SectionFrame(Frame):
    
    help_info = static['boardlist'][0] + '\r\n'
    thead    = (static['boardlist'][1], static['boardlist'][2])
    p_format = (static['boardlist'][3], static['boardlist'][4])

    class TableMap:
        
        def __init__(self,data):
            self.data = data
            self.len = len(data)
            
        def __getitem__(self,key):
            board = self.data[key]
            return {
                "total":board.get_total(),
                "boardname":board['boardname'],
                "number":key,
                "type":'',
                "reproduced":'',
                "description":board['description'],
                'online':0,
                'unknow':'',
                'bm': board['bm'] and ' '.join(board['bm'].split(':')),
                'have_news':'',
                }
        def __len__(self):
            return self.len
                

    def initialize(self,section_name='Test',mode=0):
        self.write(str_top(self,u'[讨论区列表]'))
        self.write(self.help_info)
        self.mode = mode
        self.write(self.thead[mode])
        self.data = self.TableMap(db_orm.get_section(section_name).get_allboards())
        self.table = self.sub(Table,self.p_format[mode],line=4,data=self.data)
        self.table.do_refresh()
        
