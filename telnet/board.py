# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
    
from chaofeng import Frame,EndInterrupt,Timeout
from chaofeng.g import mark,static
from chaofeng.ui import TextInput,Password,Animation,ColMenu,Table
from datetime import datetime
import config
import chaofeng.ascii as ac
from lib import get_boardlist_q

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

    def __init__(self,frame,format_str,data,line=0):
        Table.__init__(self,frame,format_str,line=line,data=data,limit=5)
        self.buf = []

    def send(self,data):
        Table.send(self,data)
        if data.isdigit() :
            self.buf.append(data)

class AllDataMap:

    def __init__(self,data):
        self._data = data

    def __getitem__(self,key):
        data = self._data[key]
        return (data["total"],u"◆",data["descript"],data["type"],u"○",u"没有中文叙述",2012,'',u"SYSOP")

    def __len__(self):
        return len(self._data)

COUNTER = 0
    
class NewDataMap:

    def __init__(self,data):
        self._data = data

    def __getitem__(self,key):
        data = self._data[key]
        global COUNTER
        COUNTER += 1
        return (COUNTER,data["descript"],data["type"],u"○",u"没有中文叙述",2012,'',u"SYSOP")

    def __len__(self):
        return len(self._data)

@mark('boardlist')
class BoardListFrame(Frame):
    '''
    实现讨论区列表。

    @para sid : 分类编号为sid的讨论区
    @para new : 有新文章发布的讨论区
    '''
    nav_info  = static['boardlist'][0]
    help_info = static['boardlist'][1]
    foot_info = static['boardlist'][4]
    thead    = (static['boardlist'][2],static['boardlist'][3])
    p_format = (static['boardlist'][5],static['boardlist'][6])
    m_map    = (AllDataMap,NewDataMap)
    
    # Show All Mode : 0
    # Show New Mode : 1
    
    def initialize(self,sid=0,new=None,limit=20):
        self.sid = sid
        self.data = get_boardlist_q(sid)

        #todo : get pos info
        info_format = "%s区 [%s]"
        pos = self.session.get('pos')
        if not pos :
            pos = ''
            pos_info = ''
        else:
            pos_info = self.info_format % (self.session['pos_num'],
                                           self.session['boardname'])
        self.write(self.nav_info % { "pos_info" : pos_info })
        self.write('\r\n' + self.help_info + '\r\n' )

        self.mode = 1 if new else 0
        self.write(self.thead[self.mode]+ac.reset)
        self.mdata = self.m_map[self.mode](self.data)
        self.format = self.p_format[self.mode]
        self.table = BoardListTable(self,self.format,self.mdata,line=4)

    def set_mode(self,mode):
        self.mode = mode
        self.write(ac.save+ac.move2(3,0)+self.thead[mode]+ac.reset+ac.restore)
        self.mdata = self.m_map[mode](self.data)
        self.format = self.p_format[mode]
        self.table.format = self.p_format[mode]
        self.table.data = self.mdata
        self.table.refresh()
        
    def get(self,data):
        for c in data :
            print ord(c),
        print
        self.table.send(data)
        if data == 'c' :
            self.set_mode(1 - self.mode)
        elif data == '/' :
            #todo : search
            pass
        elif data == 'z' :
            #todo : 设置隐藏
            pass
        elif data == 'y' :
            #todo : 显示全部讨论区或不显示
            pass
        elif data == 's' :
            #todo : sort
            pass
        elif data == 'L' :
            #todo : 查看全部信息
            pass
        elif data == 'S' :
            #todo : 发信
            pass
        elif data == 'f' :
            #todo : 寻找好友
            pass
        elif data == '!' :
            self.goto(mark['bye'])
        elif data == '^Z' :
            #todo : 回或看讯息 ？？？？
            pass
        elif data == 'H' : #十大
            self.goto(mark['top-ten'])
            pass
        elif data == 'u' :
            #todo : 查询网友
            pass
        elif data == 'l' :
            #todo : 邮件选单
            pass
        elif data == ac.k_c_a :
            #todo : 版面属性
            pass
        elif data == 'X' :
            #todo : 设置只读（站务）
            pass
        elif data == ac.k_ctrl_e :
            #todo : 修改版面属性（站务）
            pass
