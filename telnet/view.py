#!/usr/bin/python2
# -*- coding: utf-8 -*-

from chaofeng import PluginHolder
from chaofeng.g import mark
from chaofeng.ui import SimpleTextBox
import chaofeng.ascii as ac
from model import manager
from libframe import BaseAuthedFrame
import logging

logger = logging.getLogger('@view')

class TextBox(SimpleTextBox):

    def message(self, message):
        self.frame.bottom_bar(message=message, s=self.s, h=self.h)

    def fix_bottom(self):
        self.message(u'')

class BaseTextBoxFrame(BaseAuthedFrame):

    plugins = PluginHolder(
        )

    shortcuts = {
        ac.k_left:"finish",
        }

    shortcuts_ui = {
        ac.k_up : "move_up",
        "k":"move_up",
        ac.k_down : "move_down",
        " ":"move_down",
        ac.k_right:"move_down",
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

    def restore(self):
        self._textbox.restore_screen()

    def restore_screen(self):
        self._textbox.restore_screen()

    def reset_text(self, text, spoint=0):
        self._textbox.reset_text(text, spoint)
        self.restore_screen()

    def getscreen(self):
        return self._textbox.getscreen()

    def bottom_bar(self, s, h, message=''):
        self.write(ac.move2(24,1))
        self.render(u'bottom_view', s=s, h=h, message=message)

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

@mark('_view_post_o')
class ViewPostFrame(BaseTextBoxFrame):

    shortcuts = BaseTextBoxFrame.shortcuts.copy()
    shortcuts.update({
            ac.k_ctrl_x:"same_topic_view",
        })

    def initialize(self, post):
        self.post = post
        assert post['bid'] == self.session['last_board_attr']['bid']
        self.next_loader, self.prev_loader = manager.post.get_post_loader(
            self.session['last_board_attr']['boardname'])
        self.setup(self.wrapper_post(post))

    def finish(self, e=None):
        logger.debug('finish - [%s]', e)
        if e is None:
            self.session['board_flash'] = self.post['pid']
            self.goto_back()
        if e is True:
            post = self.next_loader(self.post['pid'])
        else :
            post = self.prev_loader(self.post['pid'])
        if not post:
            self.session['board_flash'] = self.post['pid']
            self.goto_back()
        self.post = post
        self.reset_text(self.wrapper_post(self.post), 0)

    def same_topic_view(self):
        self.goto('_view_topic_post_o', post=self.post)

@mark('_view_topic_post_o')
class ViewPostSameTopic(BaseTextBoxFrame):

    def initialize(self, post):
        logger.debug('enter topic view')
        self.post = post
        board = self.session['last_board_attr']
        assert post['bid'] == board['bid']
        self.next_loader, self.prev_loader = manager.post.get_topic_post_loader(
            board['boardname'], post['tid'])
        self.setup(self.wrapper_post(post))

    def finish(self, e=None):
        logger.debug('topic mode %s', e)
        if e is None:
            logger.debug('topic mode end')
            self.session['board_flash'] = self.post['pid']
            self.goto_back()
        if e is True:
            post = self.next_loader(self.post['pid'])
            if post is None:
                self.session['board_flash'] = self.post['pid']
                self.goto_back()
        else :
            post = self.prev_loader(self.post['pid'])
            if not post:
                return
        logger.debug('post %s', post)
        self.post = post
        self.reset_text(self.wrapper_post(post))
        
    def bottom_bar(self, s, h, message=''):
        self.write(ac.move2(24,1))
        self.render(u'bottom_view_topic', s=s, h=h, message=message)
        
@mark('help')
class TutorialFrame(BaseTextBoxFrame):

    def initialize(self, pagename='index'):
        self.history.append(u'帮助 - [\%s]' % pagename)
        self.setup(text=self.get_help_page(pagename))

    def finish(self, e=None):
        self.goto_back()

# from chaofeng.g import mark
# from chaofeng.ui import Animation,LongTextBox,TextEditor,NullValueError
# from chaofeng import ascii as ac
# from libframe import BaseAuthedFrame,BaseTextBoxFrame
# from model import manager
# from datetime import datetime
# from libdecorator import need_perm
# import config
# import re

# @mark('view_text')
# class ViewTextFrame(BaseTextBoxFrame):

#     def get_text(self):
#         return self.text

#     def initialize(self, text):
#         self.text = text
#         super(ViewTextFrame, self).initialize()
        
# @mark('post')
# class ReadPostFrame(BaseTextBoxFrame):

#     hotkeys = {
#         "R":"reply",
#         "r":"reply",
#         }

#     @staticmethod
#     def try_jump(self,args):
#         try:
#             r = manager.query.get_board_ability(self.userid, args[0])[0]
#             if r and manager.post.get_post(args[0], args[1]) :
#                 return dict(boardname=args[0],
#                             pid=args[1])
#         except :
#             return False

#     def get_post(self, board, pid):
#         return manager.post.get_post(board['boardname'], pid)

#     def wrapper_post(self,post):
#         return self.render_str('post-t',post=post)

#     def get_text(self):
#         return self.text

#     def check_perm(self, boardname, pid):
#         r = manager.query.get_board_ability(self.session.user.userid, boardname)[0]
#         return r or u"错误的讨论区或你没有权限！"

#     @need_perm
#     def initialize(self, boardname, pid):
#         # if not (hasattr(self.session, 'lastboard') and \
#                 # getattr(self.session, 'lastboard')) or \
#                 # self.session.lastboard.boardname != boardname :
#         # manager.action.enter_board(self.seid, boardname)
#             # try:
#                 # index = map(lambda x:x['boardname'], self.boards).index(boardname)
#             # except ValueError:  ############  impossible
#                 # self.pause()
#                 # self.goto_back()
#         # self.session.lastboard = manager.board.get_board(boardname)
#         self.board = board = manager.board.get_board(boardname)
#         try:
#             self._read_post(board['boardname'], pid)
#         except NullValueError as e:
#             self.write(e.message)
#             self.pause()
#             self.goto_back()
#         super(ReadPostFrame,self).initialize()

#     def _read_post(self, boardname, pid):
#         post = self.get_post(self.board, pid)
#         if post :
#             self.boardname, self.pid = boardname, pid
#             self.post = self.get_post(self.board, pid)
#             self.session['lastboard'] = boardname
#             self.session['lastpid'] = pid
#             self.session['lasttid'] = self.post.tid
#             self.text = self.wrapper_post(self.post)
#             self.history.append(u'文章 - %s 版 - [%s](/p/%s/%s)' % \
#                                     (boardname, self.post['title'], boardname,
#                                      self.post['pid']))
#             manager.readmark.set_read(self.userid, self.boardname, self.pid)
#         else:
#             raise NullValueError(u'没有此文章')

#     def reset_post(self, boardname, pid):
#         if pid is not None :  ###################  None to return
#             self._read_post(boardname, pid)
#             self.reset_text(self.text)
#         else:
#             self.goto_back()

#     def next_post(self):
#         return self.boardname, manager.post.next_post_pid(self.boardname,self.pid)

#     def prev_post(self):
#         return self.boardname, manager.post.prev_post_pid(self.boardname,self.pid)

#     def finish(self,args=None):
#         if args is None:
#             self.goto_back()
#         if args is True:
#             self.reset_post(*self.next_post())
#         if args is False:
#             self.reset_post(*self.prev_post())

#     def goto_back(self):
#         board = manager.board.get_board(self.boardname)
#         index = manager.post.get_rank_num(self.boardname, self.pid)
#         self.goto('board', board=board, default=index)

#     def reply(self):
#         _,w,_,_ = manager.query.get_board_ability(self.userid,
#                                                   self.board['boardname'])
#         w = w and self.post.replyable
#         if w :
#             self.suspend('reply_post', boardname=self.boardname, post=self.post)
#         else:
#             self.message(u'该文章禁止回复！')

#     def get(self, char):
#         if char in ac.ks_finish:
#             self.finish(True)
#         self.textbox.do_command(config.hotkeys['view_textbox'].get(char))
#         self.do_command(config.hotkeys['view'].get(char))
#         self.do_command(self.hotkeys.get(char))

# @mark('view_clipboard')
# class ViewClipboardFrame(BaseTextBoxFrame):

#     def get_text(self):
#         return manager.clipboard.get_clipboard(self.userid)

#     def finish(self, a=None):
#         self.goto_back()

# @mark('help')
# class TutorialFrame(BaseTextBoxFrame):

#     @staticmethod
#     def try_jump(self, args):
#         if 'help/%s' % args[0] in config.all_help_file :
#             return dict(page=args[0])

#     def initialize(self,page='index'):
#         self.page = page
#         self.history.append(u'帮助 - [%s](/h/%s)' % (self.page, self.page))
#         super(TutorialFrame,self).initialize()

#     def get_text(self):
#         return self.render_str('help/%s' % self.page)

#     def finish(self,args=None):
#         self.goto_back()

# @mark('notice_box')
# class NoticeBox(BaseTextBoxFrame):

#     def get_text(self):
#         notices=manager.notice.get_notice(self.userid, 0, 10)
#         return self.render_str('notice_box', total=self.total,
#                                notices=notices)

#     def finish(self, args=None):
#         self.goto_back()

#     def initialize(self):
#         self.total = manager.notify.check_notice_notify(self.userid) or 0
#         manager.notify.clear_notice_notify(self.userid)
#         super(NoticeBox, self).initialize()

