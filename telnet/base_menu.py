# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
    
from chaofeng import BindFrame
from chaofeng.g import mark,static,_w
from chaofeng.ui import Animation,ColMenu
import config
import chaofeng.ascii as ac
from libtelnet import str_top,str_bottom

class BaseMenuFrame(BindFrame):
    
    '''
    浏览全部菜单的类。菜单的名字通过name在调用initialize时传入。
    将会以session['pos']和session['board_num']和session['boardname']作为
    当前所在的位置，讨论区的编号，讨论区的名字输出。
    电子公告版取active.ani作为内容。
    online和online_friend用于输出在线人数（未实现）。
    利用config中的menu[name]来设置菜单(ColMenu类),eg :
       ( (fram_mark,goto_kwargs),shortcuts, [ (pos_l,pos_r) ] )
       ...
    其中frame_mark表示将会跳转到mark[frame_mark]，goto_kwargs是跳转时的
    参数，是一个字典，shortcuts是快捷键。如果需要，可以加入 (pos_l,pos_r)
    表示这个菜单项的位置，如果不加，默认在上一项的下面。

    keypoint:
         static['active'] 为电子公告板的内容
         config.menu[name] 为该菜单的相关设定
         static['menu_'+name] 为该菜单显示的内容（包括背景和菜单字）

    @para name : 表示这个菜单的名字，将会加载与名字相关的内容。应该为
                 英文
    '''

    def initialize(self,content,config_data):
        self.anim = self.sub(Animation,static['active'],start=3,run=True)
        self.write(ac.clear+str_top(self))
        self.content = content
        self.menu = self.sub(ColMenu,config_data)
        self.do_refresh()
        value = self.menu.read_until()
        if isinstance(value,str) :
            next_f = value
            kwargs = {}
        else : next_f,kwargs = value
        self.goto(mark[next_f],**kwargs)

    def do_refresh(self):
        self.write(ac.move2(11,0)+self.content)
        self.write(ac.move2(24,0)+str_bottom(self))
        self.menu.refresh()
        
