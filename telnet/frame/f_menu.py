# -*- coding: utf-8 -*-
from chaofeng import Frame,launch
from chaofeng.g import mark,static
from chaofeng.ui import Animation,ColMenu
from datetime import datetime
import config

class BaseFrame(Frame):

    background = static['base'].safe_substitute(
        pos=u'%-10s',
        pos_info = u'%10s',
        content = u'%s',
        time='%s',
        online=u'%4d',
        online_friend=u'%3d',
        username=u'%s',
        )

    def initialize(self,pos,pos_num,pos_name=u''):
        self.write(self.background % (
                pos,
                (u'%d区 [%s]' % (pos_num,pos_name)),
                self.content,
                datetime.today().ctime(),
                1,
                2,
                u'LTaoist'))

class BaseMenu(BaseFrame):

    def initialize(self):
        self.anim = Animation(self,static['active'],start=3)
        self.content = self.anim.fetch()[0] + self.content
        super(BaseMenu,self).initialize('0',0,'0')
        self.anim.run_bg()

@mark('main')
class MainMenu(BaseMenu):

    content = static['main_menu']
    menu = config.menu['main']

    def initialize(self):
        super(MainMenu,self).initialize()
        self.goto(marks[ColMenu(self,self.menu).read()])

@mark('category')
class CatMenu(BaseMenu):

    content = static['cat_menu']
    menu = config.menu['cat']

    def initialize(self):
        super(CatMenu,self).initialize()
        cid = ColMenu(self,self.menu,height=10).read()
        self.goto(marks['boardlist'],cid=cid)
