# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import Frame,BindFrame,static,EndInterrupt
from chaofeng.g import mark
from chaofeng.ui import Table,TextBox,TextEditor
from chaofeng import ascii as ac
from libtelnet import str_top,str_bottom
from model import *
from datetime import datetime
import config
import re

@mark('boardlist')
class BoardListFrame(Table):
    
    help_info = static['boardlist'][0] + '\r\n'
    thead    = (static['boardlist'][1], static['boardlist'][2])
    p_format = (static['boardlist'][3], static['boardlist'][4])
    shortcuts = config.default_shortcuts

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
        self.write(ac.clear)
        self.write(str_top(self,u'[讨论区列表]'))
        self.write(self.help_info)
        self.write(self.thead[mode])
        self.write(ac.move2(24,0)+str_bottom(self))
        self.mode = mode
        self.data = self.TableMap(
            db_orm.get_section(section_name).get_allboards())
        super(BoardListFrame,self).initialize(
            self.p_format[mode],line=4,data=self.data)

    def do_boardlist_change_mode(self):
        self.mode = 1 - self.mode
        self.write(ac.move2(3,0)+self.thead[self.mode])
        self.set_format(self.p_format[self.mode])

    def get(self,data):
        super(BoardListFrame,self).get(data)
        if data in ac.ks_finish :
            f = self.data[self.fetch()]['boardname']
            self.goto(mark['board'],boardname=f)
        
@mark('board')
class BoardFrame(Table):
    
    help_info = static['board'][0] + '\r\n' + static['board'][1]
    li_format = static['board'][2]
    shortcuts = config.default_shortcuts

    class BoardMap:

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
            d = self.get_post(key).dump_attr()
            d['number'] = key
            d['data'] = ''
            return d

        def __len__(self):
            return self.len
            
    def initialize(self,boardname):
        self.session['last_boardname'] = boardname
        self.data = db_orm.get_board(boardname)
        self.w_data = self.BoardMap(self.data)
        self.write(ac.clear+str_top(self,self.data['bm'],boardname))
        self.write(self.help_info)
        self.write(ac.move2(24,0)+str_bottom(self))
        super(BoardFrame,self).initialize(self.li_format,line=4,
                                            data=self.w_data)

    def get(self,data):
        super(BoardFrame,self).get(data)
        if data in ac.ks_finish :
            postobj = self.w_data.get_post(self.fetch())
            if postobj :
                self.goto(mark['post'],postobj=postobj)
        elif data == ac.k_c_p :
            self.goto(mark['add_post'],boardobj=self.data)

@mark('post')
class PostFrame(TextBox):

    def initialize(self,postobj):
        self.body = postobj
        super(PostFrame,self).initialize(postobj['content'])

    def get(self,data):
        super(PostFrame,self).get(data)
        if data == ac.k_ctrl_c :
            self.goto(mark['board'],boardname=self.session['last_boardname'])

@mark('add_post')
class AddPostFrame(TextEditor):

    re_c = re.compile('[^\r\n]+')

    def initialize(self,boardobj):
        self.write(ac.clear)
        self.board = boardobj
        self.body = Post(dict(
                bid=boardobj['bid'],
                owner=self.session['userid'],
                fromaddr=self.session['ip']))        
        super(AddPostFrame,self).initialize()
        self.get(ac.k_ctrl_l)

    def get(self,data):
        super(AddPostFrame,self).get(self,data)

    def do_cancel(self):
        self.write(ac.move2(24,0)+u'按下y确认发布，Ctrl+C离开')
        c =  self.static_read()
        if c == 'y':
            print repr(self.re_c)
            print repr(self.buf[0])
            title_re = re.match(self.re_c,''.join(self.buf[0]))
            if not title_re  :
                self.write(u'错误的标题！')
                return
            self.body['title'] = title_re.group(0)
            self.body['content'] = self.fetch()
            self.write(u'\r\n 标题 : %s \r\n' % self.body['title'])
            self.board.add_post(self.body)
            self.write(u'发帖成功！')
            self.pause()
            self.goto(mark['board'],boardname=self.board['boardname'])
        elif c == ac.k_ctrl_c :
            self.goto(mark['board'],board['boardname'])
        
# todo :
# better wrap up for UI,Frame, and Frame,get
