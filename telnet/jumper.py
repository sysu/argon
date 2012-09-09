#!/usr/bin/env python 
#*- encoding: utf8 -*-

import re
from chaofeng.g import mark
import chaofeng.ascii as ac
from view import BaseTextBoxFrame
from model import manager
import config

plugins = BaseTextBoxFrame.plugins

re_post = re.compile(ur'\[(\w{2,20})/(\d{1,8})\]|\[\\(\w{2,20})\]')

def display_mark(match):
    if match[0] :
        return u'前往到 %s 的第 %s 号文？' % (match[0], match[1])
    else:
        return u'前往 %s 的帮助？' % match[2]
    
@BaseTextBoxFrame.plugins.add_action(ac.k_ctrl_r)
def jummp_from_screen(frame):
    text = frame.getscreen()
    options = re_post.findall(text)
    if not options :
        return
    op = frame.select(lambda op : frame.message(display_mark(op)),
                     options)
    if op is False:
        frame.fix_bottom()
        return
    op = options[op]
    if op[0] :
        perm = manager.query.get_board_ability(frame.userid, op[0])
        if not perm[0] :
            frame.message(u'错误的跳转标记')
            frame.pause()
            frame.fix_bottom()
            return
        frame.suspend('plugin_jumpper:view_post_float',
                      boardname=op[0],
                      pid=op[1])
    elif 'help/%s' % op[2] in config.all_help_file :
        frame.suspend('help', pagename=op[2])

@mark('plugin_jumpper:view_post_float')
class ViewPostFloatFrame(BaseTextBoxFrame):

    shortcuts = BaseTextBoxFrame.shortcuts.copy()
    shortcuts.update({
            ac.k_ctrl_o:"goto_board",
            })

    def initialize(self, boardname, pid):
        self.boardname = boardname
        perm = manager.query.get_board_ability(self.userid, boardname)
        if not perm[0] :
            self.goto_back()
        post = manager.post.get_post(boardname, pid)
        if post :
            self.setup(self.wrapper_post(post))
        else:
            self.goto_back()

    def finish(self, e=None):
        self.goto_back()        

    def bottom_bar(self, s, h, message=''):
        self.write(ac.move2(24, 1))
        self.render(u'bottom_view_float', s=s, h=h, message=message)

    def goto_board(self):
        board = manager.board.get_board(self.boardname)
        board.perm = manager.query.get_board_ability(self.userid, self.boardname)
        self.suspend('_board_o', board=board)
