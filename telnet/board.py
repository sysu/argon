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

class PostMap:

    def __init__(self,t_boardobj):
        self.tb = t_boardobj

    @staticmethod
    def wrap_up(data):
        return ( data['pid'],data['flag'],data['owner'],data['posttime'],data['title'] )

    def __getitem__(self,key):
        return self.wrap_up(self.tb[key])

    def __len__(self):
        return len(self.tb)

@mark('boardlist')
class SectionFrame(Frame):
    '''
    实现讨论区列表。

    @para sid : 分类编号为sid的讨论区
    @para new : 有新文章发布的讨论区
    '''
    help_info = static['boardlist'][0] + '\r\n'
    thead    = (static['boardlist'][1], static['boardlist'][2])
    p_format = (static['boardlist'][3], static['boardlist'][4])
    m_map    = (AllDataMap,NewDataMap)

    def initialize(self,sid=0):
        self.body = Section(sid)

@mark('board')
class BoardFrame(Frame):

    '''
    版块文章浏览。

    @goto : post ( num=index, t_board )
    @para boardname : 要浏览的版块的名称
    '''

    help_info = static['board'][0] + '\r\n' + static['board'][1]
    li_format = static['board'][2]

    def initialize(self,boardname=u"Test"):

        self.session['lastboard'] = boardname

        self.body = TBoard(Board(boardname))
        self.data = PostMap(self.body)

        self.write(ac.clear+str_top(self,'bm',boardname))
        self.write(self.help_info)
        self.write(ac.move2(24,0)+str_bottom(self))

        self.table = self.sub(Table,self.li_format,data=self.data,line=4)
        res = self.table.read_until()
        self.goto(mark['post'],num=res,t_board=self.body)

    def get(self,data):
        print repr(data)
        if data == ac.k_c_c :
            self.close()
        if data == ac.k_c_p :
            self.goto(mark['editpost'],board=self.body.body)

@mark('post')
class PostFrame(Frame):

    def initialize(self,body=None,num=0,t_board=None):
        if body is None :
            body = t_board[num]
        self.body = body
        self.box = self.sub(TextBox,self.body["content"])

    def get(self,data):
        self.box.get(data)
        if data == ac.k_left :
            self.goto(mark['board'])

@mark('editpost')
class EditPostFrame(Frame):

    def initialize(self,board):
        self.editor = self.sub(TextEditor,text='Test')
        p = {}
        p["bid"] = board.bid
        p["content"] = self.editor.read_until(termitor=ac.k_c_c)
        p["owner"] = self.session["username"]
        # p["posttime"] = datetime.now()
        p["title"] = u"Hello,Test"
        p["flag"] = 88
        board.add_post(Post(p))
        self.goto(mark["board"])
