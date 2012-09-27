#!/usr/bin/python2
# -*- coding: utf-8 -*-

from chaofeng import PluginHolder
from chaofeng.g import mark
from chaofeng.ui import SimpleTextBox
import chaofeng.ascii as ac
from model import manager
from libframe import BaseAuthedFrame
from libformat import style2telnet
import logging

logger = logging.getLogger('@view')

class TextBox(SimpleTextBox):

    def message(self, message):
        self.frame.bottom_bar(message=message, s=self.s, l=self.max)

    def fix_bottom(self):
        self.message(u'')

class BaseTextBoxFrame(BaseAuthedFrame):

    plugins = PluginHolder(
        )

    shortcuts = {
        ac.k_left:"finish",
        "h":"show_help",
        }

    shortcuts_ui = {
        ac.k_up : "move_up",
        "k":"move_up",
        ac.k_down : "move_down",
        " ":"move_down",
        "j":"move_down",
        ac.k_ctrl_b:"page_up",
        ac.k_page_up:"page_up",
        ac.k_ctrl_f:"page_down",
        ac.k_page_down:"page_down",
        ac.k_right:"page_down",
        ac.k_home:"goto_first",
        ac.k_end:"goto_last",
        "$":"goto_last",
        }

    def finish(self, e=None):
        raise NotImplementedError

    def setup(self, text):
        self._textbox = self.load(TextBox, text, self.finish)
        self.restore_screen()

    def get(self, char):
        if char in self.shortcuts :
            self.do_command(self.shortcuts[char])
        elif char in self.shortcuts_ui :
            self._textbox.do_command(self.shortcuts_ui[char])
        else :
            self.plugins.do_action_ifex(char, self)
            if self._textbox.is_last() :
                self.finish(None)

    def restore(self):
        self._textbox.restore_screen()

    def restore_screen(self):
        self._textbox.restore_screen()

    def reset_text(self, text, spoint=0):
        self._textbox.reset_text(text, spoint)
        self.restore_screen()

    def getscreen(self):
        return self._textbox.getscreen()

    def bottom_bar(self, s, l, message=''):
        self.write(ac.move2(24,1))
        percent = (s+1)*100 // (l+1) ;
        self.render(u'bottom_view', s=s, percent=percent, message=message)

    def message(self, msg):
        self.push(ac.move2(24, 1))
        self.push(ac.kill_line)
        self.push(msg)

    def fix_bottom(self):
        self._textbox.fix_bottom()

    def wrapper_post(self, post):
        return self.render_str('post-t', post=post)

    def get_help_page(self, pagename):
        return self.render_str('/help/%s' % pagename)

    def show_help(self):
        self.suspend('help', pagename='view')
        
@mark('_view_post_o')
class ViewPostFrame(BaseTextBoxFrame):

    plugin = PluginHolder()

    shortcuts = BaseTextBoxFrame.shortcuts.copy()
    shortcuts.update({
            ac.k_ctrl_x:"same_topic_view",
            "r":"reply_post",
            "R":"reply_post",
        })

    def initialize(self, post, cond=''):
        manager.status.set_status(self.seid,
                                  manager.status.READING)
        self.post = post
        # assert post['bid'] == self.session['last_board_attr']['bid']
        if cond :
            self.next_loader, self.prev_loader = \
                manager.post.get_cond_post_loader(
                self.session['lastboardname'],
                cond)
        else:
            self.next_loader, self.prev_loader = manager.post.get_post_loader(
                self.session['lastboardname'])
        manager.readmark.set_read(self.userid,
                                  self.session['lastboardname'],
                                  post['pid'])
        self.setup(self.wrapper_post(post))

    def finish(self, e=None):
        logger.debug('finish - [%s]', e)
        if e is None:
            self.session['lastpid'] = self.post['pid']
            self.goto_back()
        if e is True:
            post = self.next_loader(self.post['pid'])
        else :
            post = self.prev_loader(self.post['pid'])
        if not post:
            self.session['lastpid'] = self.post['pid']
            self.goto_back()
        self.post = post
        manager.readmark.set_read(self.userid,
                                  self.session['lastboardname'],
                                  post['pid'])
        text = self.wrapper_post(self.post)
        text = style2telnet(text)
        self.reset_text(text, 0)

    def same_topic_view(self):
        self.goto('_view_topic_post_o', post=self.post)

    def reply_post(self):
        boardname = self.session['lastboardname']
        # assert boardname == self.post['bid']
        post = self.post
        perm = manager.query.get_board_ability(self.userid,
                                               boardname)
        if perm[1] and post['replyable'] :
            self.suspend('_reply_post_o',
                         boardname=boardname,
                         post=post)
        else:
            self.cls()
            self.write(u'你没有发文权限或本文禁止回复！\r\n')
            self.restore_screen()

@mark('_view_topic_post_o')
class ViewPostSameTopic(BaseTextBoxFrame):

    def initialize(self, post):        
        logger.debug('enter topic view')
        self.post = post
        # board = self.session['last_board_attr']
        # assert post['bid'] == board['bid']
        self.next_loader, self.prev_loader = manager.post.get_topic_post_loader(
            self.session['lastboardname'], post['tid'])
        manager.readmark.set_read(self.userid,
                                  self.session['lastboardname'],
                                  post['pid'])
        self.setup(self.wrapper_post(post))

    def finish(self, e=None):
        logger.debug('topic mode %s', e)
        if e is None:
            logger.debug('topic mode end')
            self.session['lastpid'] = self.post['pid']
            self.goto_back()
        if e is True:
            post = self.next_loader(self.post['pid'])
            if post is None:
                self.session['lastpid'] = self.post['pid']
                self.goto_back()
        else :
            post = self.prev_loader(self.post['pid'])
            if not post:
                return
        logger.debug('post %s', post)
        self.post = post
        manager.readmark.set_read(self.userid,
                                  self.session['lastboardname'],
                                  post['pid'])
        self.reset_text(self.wrapper_post(post))
        
    def bottom_bar(self, s, l, message=''):
        self.write(ac.move2(24,1))
        percent = (s+1)*100 // (l+1) ;
        self.render(u'bottom_view_topic', s=s, percent=percent,
                    message=message)
        
@mark('help')
class TutorialFrame(BaseTextBoxFrame):

    def initialize(self, pagename='index'):
        manager.status.set_status(self.seid,
                                  manager.status.RHELP)
        self.history.append(u'帮助 - [\%s]' % pagename)
        self.setup(text=self.get_help_page(pagename))

    def finish(self, e=None):
        self.goto_back()

    def show_help(self):
        self.suspend('help', pagename='help')

@mark('_query_board_o')
class QueryBoardFrame(BaseTextBoxFrame):

    def initialize(self, board):
        total = manager.post.get_posts_total(board['boardname'])
        text = self.render_str('board-t', total=total, **board)
        self.setup(text=text)

    def finish(self, e=None):
        self.goto_back()

