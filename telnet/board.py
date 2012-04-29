# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
    
from chaofeng import Frame,EndInterrupt,Timeout
from chaofeng.g import mark,static,_s,_u,_w
from chaofeng.ui import TextInput,Password,Animation,ColMenu,Table
from datetime import datetime
import config
import chaofeng.ascii as ac
from lib import get_boardlist_q
from libtelnet import str_top,str_bottom

'''
实现讨论区相关的Frame。

'''

class AllDataMap:

    def __init__(self,data):
        self._data = data

    def __getitem__(self,key):
        data = self._data[key]
        return (data["total"],u"◆",data["descript"],data["type"],u"○",u"没有中文叙述",2012,'',u"SYSOP")

    def __len__(self):
        return len(self._data)

class NewDataMap:

    def __init__(self,data):
        self._data = data

    def __getitem__(self,key):
        data = self._data[key]
        return (key,data["descript"],data["type"],u"○",u"没有中文叙述",2012,'',u"SYSOP")

    def __len__(self):
        return len(self._data)

@mark('boardlist')
class BoardListFrame(Frame):
    '''
    实现讨论区列表。

    @para sid : 分类编号为sid的讨论区
    @para new : 有新文章发布的讨论区
    '''
    help_info = static['boardlist'][0] + '\r\n'
    thead    = (static['boardlist'][1], static['boardlist'][2])
    p_format = (static['boardlist'][3], static['boardlist'][4])
    m_map    = (AllDataMap,NewDataMap)
    
    # Show All Mode : 0
    # Show New Mode : 1
    
    def initialize(self,sid=0,new=None,limit=20):
        self.session['username'] = 'Tester'
        self.sid = sid
        self.limit = limit
        self.data = get_boardlist_q(sid)
        self.table = None
        self.write(str_top(self,u'[讨论区列表]'))
        self.write(self.help_info)
        self.write(ac.move2(24,0) + str_bottom(self))
        self.set_mode(1 if new else 0)
        
    def set_mode(self,mode):
        self.mode = mode
        self.mdata = self.m_map[mode](self.data)
        self.format = self.p_format[mode]
        if self.table :
            self.table.format = self.p_format[mode]
            self.table.data = self.mdata
            self.write(ac.save+ac.move2(3,0)+self.thead[mode]+ac.reset+ac.restore)
            self.table.refresh()
        else :
            self.write(ac.move2(3,0)+self.thead[mode]+'\r\n')
            self.table = Table(self,self.format,data=self.mdata,line=4,limit=self.limit)
        
    def get(self,data):
        for c in data :
            print ord(c),
        print
        self.table.send(data)
        if data == 'c' :
            self.set_mode(1 - self.mode)
        elif data in ['k','p'] :
            self.table.move_up()
        elif data == 'j' :
            self.table.move_down()
        elif data == ['p',ac.k_ctrl_b,'b'] :
            self.table.page_up()
        elif data == ['n',ac.k_ctrl_f,' ']:
            self.table.page_down()
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

@mark('board')
class BoardFrame(Frame):

    # help_info = static['board_info']

    def initialize(self,boardname=u"Test"):
        self.session['username'] = 'Tester'
        self.write(str_top(self,boardname))
        self.write(help_info)
        # self.table = 
        self.write(str_bottom(self))
