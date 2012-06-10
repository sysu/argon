# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import static,mark
from chaofeng.ui import TextEditor
from model import manager
from argo_frame import ArgoFrame
from libtelnet import zh_format
from datetime import datetime
import config

class ArgoEditor(TextEditor):

    bottom_text = ac.move2(24,0) + static['bottom'][1]

    def bottom_bar(self,msg=''):
        self.write(zh_format(self.bottom_text,
                             msg or u'现在的时间是【%s】'% datetime.now().ctime(),
                             self.l,self.r))
        self.fix_cursor()

class EditFrame(ArgoFrame):

    key_editor = {
        ac.k_up:"move_up",          ac.k_ctrl_p:"move_up",
        ac.k_down:"move_down",      ac.k_ctrl_n:"move_down",
        ac.k_left:"move_left",
        ac.k_right:"move_right",    ac.k_ctrl_v:"move_right",
        ac.k_home:"move_line_beginning", ac.k_ctrl_a:"move_line_beginning",
        ac.k_ctrl_k:"kill_to_end",  ac.k_ctrl_e:"move_line_end",
        ac.k_ctrl_b:"page_up",      ac.k_page_up:"page_up",
        ac.k_ctrl_f:"page_down",    ac.k_page_down:"page_down",
        ac.k_backspace:"backspace", ac.k_ctrl_h:"backspace",
        ac.k_del:"delete",          ac.k_ctrl_d:"delete",
        ac.k_delete:"delete",
        ac.k_ctrl_y:"kill_whole_line",
        ac.k_end:"move_line_end",
        ac.k_ctrl_s:"move_firstline",
        ac.k_ctrl_t:"move_lastline",
        
        ac.k_enter_linux:"new_line",
        ac.k_enter_window:"new_line",

        ac.k_ctrl_S2:"set_mark",

        ac.k_ctrl_f2:"save_history",
        ac.k_ctrl_g:"restore_history",
        ac.k_ctrl_l:"refresh",

        }

    key_editor_area = {
        ac.k_ctrl_d:"remove_area",
        ac.k_ctrl_u:"exchange_pos",
        ac.k_ctrl_p:"paste_area",
        ac.k_ctrl_s:"msg_select",
        }

    key_maps = {
        ac.k_ctrl_w:"finish",
        }

    REG_CMD_START = ac.k_ctrl_u

    _e = ArgoEditor(height=23,hislen=5,dis=10)

    def initialize(self):
        self.e = self.load(self._e)
        self.e.refresh_all()
        self.cls()
        
    def get(self,char):
        if char in self.key_editor:
            self.e.do_command(self.key_editor[char])
        elif char == self.REG_CMD_START:
            x = self.read_secret()
            if x in self.key_editor_area:
                self.e.do_command(self.key_editor_area[x])
        elif char in self.key_maps:
            getattr(self,self.key_maps[char])()
        else:
            self.e.safe_insert_iter(char)

    def finish(self):
        print self.e.getall()

    def message(self,content):
        self.e.bottom_bar(content[:40])

@mark('new_post')
class NewPostFrame(EditFrame):

    def initialize(self,boardname):
        self.read_title()
        super(NewPostFrame,self).initialize()
        self.boardname = boardname
        self.message(u'文章标题设置为 %s' % self.title)
        
    @property
    def status(self):
        return dict(boardname=self.boardname)

    def describe(self,s):
        return '发表文章 -- %s' % s.boardname

    def _read_title(self):
        self.write(ac.move2(24,1) + ac.kill_line + u'文章标题：')
        return self.readline()

    def read_title(self):
        d = self._read_title()
        if not d :
            self.pause(u'放弃发表文章')
            self.goto_back()
        else:
            self.title = d

    def finish(self):
        manager.action.new_post(self.boardname,
                                self.userid,
                                self.title,
                                self.e.getall(),
                                self.session.ip,
                                config.BBS_HOST_FULLNAME)
        self.message(u'发表文章成功！')
        self.pause()
        self.goto_back()

@mark('reply_post')
class ReplyPostFrame(NewPostFrame):

    def initialize(self,boardname,replyid):
        super(ReplyPostFrame,self).initialize(boardname)
        self.replyid = replyid

    @property
    def status(self):
        return dict(boardname=self.boardname,
                    replyid=self.replyid)
    
    def describe(self,s):
        return '回复文章 -- %s -- %s' % (s.boardname,s.replyid)

    def finish(self):
        manager.action.reply_post(
            self.boardname,
            self.userid,
            self.title,
            self.e.getall(),
            self.session.ip,
            config.BBS_HOST_FULLNAME,
            self.replyid)
        self.message(u'回复文章成功！')
        self.pause()
        self.goto_back()

@mark('edit_post')
class EditPostFrame(EditFrame):

    def initialize(self,boardname,pid):
        super(EditPostFrame,self).initialize()
        self.boardname = boardname
        self.pid = pid
        self.message(u'开始编辑文章')

    @property
    def status(self):
        return dict(boardname=self.boardname,
                    pid=pid)

    def describe(self,s):
        return '编辑文章 -- %s -- %s' % (s.boardname,
                                         s.pid)   

    def finish(self):
        manager.action.update_post(self.boardname,
                                   self.userid,
                                   self.pid,
                                   self.e.getall())
        self.goto_back()

