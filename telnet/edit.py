#!/usr/bin/python2
# -*- coding: utf-8 -*-

import random
from chaofeng.g import mark
from chaofeng.ui import TextEditor, TextEditorAreaMixIn
import chaofeng.ascii as ac
from libframe import BaseAuthedFrame
from model import manager
import config

class Editor(TextEditor, TextEditorAreaMixIn):

    fground_string = dict((str(x), (u'[#3%s]', u'[%#]')) for x in range(0,8))
    bground_string = dict((str(x), (u'[#4%s]', u'[%#]')) for x in range(0,8))
    special_style = {
        u'i':(u'[#3%]', u'[%#]'),
        u'u':(u'[#4%]', u'[%#]'),
        u'b':(u'[#1%]', u'[%#]'),
        u'l':(u'[#5%]', u'[%#]'),
        u'n':(u'[#7%]', u'[%#]'),
        }

    def _insert_style(self):
        self.hint(u'b) 背景色 f)字体色 r)样式复原')
        char = self.frame.read_secret()
        if char == 'b' :
            self.hint(u'背景颜色? 0)黑 1)红 2)绿 3)黄 4)深蓝 5)粉红 6)浅蓝 7)白')
            char2 = self.frame.read_secret()
            if char2 in self.bground_string :
                return self.bground_string[char2]
        elif char == 'f' :
            self.hint(u'字体颜色? 0)黑 1)红 2)绿 3)黄 4)深蓝 5)粉红 6)浅蓝 7)白')
            char2 = self.frame.read_secret()
            if char2 in self.fground_string :
                return self.fground_string[char2]
        elif char == 'e' :
            self.hint(u'特殊样式? i)斜体 u)下划线 b)加粗 l)闪烁 n)反转')
            char2 = self.frame.read_secret()
            if char2 in self.special_style:
                return self.special_style[char2]
        elif char == 'r' :
            return (u'[#%]', u'')
        elif char == ac.esc :
            return self.esc

    def insert_style(self):
        res = self._insert_style()
        if isinstance(res, tuple) :
            self.insert_string(*res)
        elif res is not None :
            self.force_insert_char(res)

    def insert_style_area(self):
        res = self._insert_style()
        if isinstance(res, tuple) :
            self.insert_string_area(*res)
                
    def bottom_bar(self,msg=u''):
        self.frame.push(ac.move2(24,1))
        self.frame.render(u'bottom_edit', message=msg,
                          l=self._hover_col, r=self._hover_row)
        self.fix_cursor()

    def do_command(self, cmd):
        getattr(self, cmd)()
        self.bottom_bar()

    def fetch_all(self):
        text = super(Editor, self).fetch_all()
        return text.replace(self.esc, ac.esc)

    def fetch_lines(self):
        text = self.fetch_all()
        return text.split('\r\n')

class BaseEditFrame(BaseAuthedFrame):

    shortcuts = {}
    shortcuts_ui = config.shortcuts['edit_ui']

    def setup(self, text, spoint=0):
        assert isinstance(text, unicode)
        self._editor = self.load(Editor, text, spoint)
        self._editor.restore_screen()
        self.bottom_bar()

    def _init_screen(self):
        self._editor.restore_screen()

    def get(self, char):
        if char in self.shortcuts:
            self.do_command(self.shortcuts.get(char))
        elif char in self.shortcuts_ui :
            self._editor.do_command(char)
        elif ac.is_safe_char(char):
            self._editor.insert_char(char)

@mark('new_post')
class NewPostFrame(BaseEditFrame):

    def update_attr(self, attrs):
        self.render('edit_head', **attrs)

    READ_ATTR_PROMPT = u"[25;1H[K[1;32m0[m~[1;32m%s[m/[1;32mx[m "\
        u"选择/随机签名档 [1;32mt[m标题，[1;32mu[m回复，[1;32mq[m放弃:"

    def read_attrs(self, sign_num, boardname, replyable ):
        attrs = {
            "boardname":boardname,
            "replyable":replyable,
            "usesign":0,
            "title":u"[正在设定主題]",
            }
        if sign_num :
            attrs['usesign'] = random.randint(1, sign_num)
        self.update_attr(attrs)
        attrs['title'] = self.safe_readline(prompt=u'请输入标题：', buf_size=40)
        if not attrs['title'] :
            return
        self.update_attr(attrs)
        prompt = self.READ_ATTR_PROMPT % sign_num
        while True:
            op = self.safe_readline(buf_size=4, prompt=prompt)
            if op == '':
                break
            elif op is False or op=='q':
                return
            elif op == 't' :
                attrs['title'] = self.safe_readline(
                    prompt=u'\r\x1b[K请输入标题：',
                    buf_size=40, #prefix=attrs['title'],
                    )
                if not attrs['title'] :
                    return
            elif op == 'u' :
                attrs['replyable'] = not attrs['replyable']
            elif op == 'x' and sign_num:
                attrs['usesign'] = random.randint(1, sign_num)
            elif op.isdigit() :
                n = int(op)
                if n <= sign_num :
                    attrs['usesign'] = n
            self.update_attr(attrs)
        return attrs

    def initialize(self, boardname):
        self.cls()
        attrs = self.read_attrs(manager.usersign.get_sign_num(self.userid),
                                boardname, True)
        if attrs :
            self.signtext = manager.usersign.get_sign(
                self.userid, attrs['usesign']-1) \
                if attrs['usesign'] else ''
            self.setup(u'')
        else:
            self.pause_back(u'放弃发表新文章')

    def finish(self):
        pass
        
# import sys
# sys.path.append('../')

# from chaofeng import ascii as ac
# from chaofeng.g import mark
# from model import manager
# from libframe import BaseAuthedFrame,BaseEditFrame, gen_quote,\
#     find_all_invert
# from datetime import datetime
# import config
# import random
# from libdecorator import need_perm
# from libformat import etelnet_to_style, style_to_etelnet

# @mark('new_post')
# class NewPostFrame(BaseEditFrame):

#     def check_perm(self, board):
#         _,w,_,_ = manager.query.get_board_ability(self.session.user.userid, board['boardname'])
#         return w or u'该版禁止发文或你没有相应的权限！'

#     @need_perm
#     def initialize(self, board):
#         self.board = board
#         self.boardname = board['boardname']
#         self.cls()
#         self.attrs = self.read_attrs()
#         if self.attrs :
#             sign = manager.usersign.get_sign(self.userid, self.attrs['usesign']-1) \
#                 if self.attrs['usesign'] else ''
#             self.signtext = sign
#             # text = self.render_str('base_post-t', sign=sign)
#             super(NewPostFrame, self).initialize()
#             self.message(u'写新文章 -- %s' % self.attrs['title'])
#         else:
#             self.write(u'放弃发表新文章')
#             self.pause()
#             self.goto_back()

#     def finish(self):
#         text = etelnet_to_style(self.fetch_all())
#         pid = manager.action.new_post(self.boardname,
#                                       self.userid,
#                                       self.attrs['title'],
#                                       text,
#                                       self.session.ip,
#                                       config.BBS_HOST_FULLNAME,
#                                       replyable=self.attrs['replyable'],
#                                       signature=self.signtext)
#         invs = find_all_invert(text)
#         if len(invs) >= 10:
#             self.message(u'你@太多人啦！')
#             self.pause()
#         else:
#             userids = []
#             for u in invs :
#                 user = manager.userinfo.get_user(u)
#                 if user :
#                     userids.append(user['userid'])
#             manager.notice.add_inve(self.userid, self.boardname,
#                                     pid, userids)
#             for u in userids:
#                 manager.notify.add_notice_notify(u)
#         index = manager.post.get_rank_num(self.boardname, pid)
#         self.goto('board', board=self.board, default=index)

# @mark('reply_post')
# class ReplyPostFrame(BaseEditFrame):

#     def check_perm(self, boardname, pid):
#         _,w,_,_ = manager.query.get_board_ability(self.session.user.userid, board['boardname'])
#         w = w and post.replyable
#         return w or u'该版禁止发文或你没有相应的权限！'

#     prompt = u'[1;32m0[m~[1;32m%s[m/[1;32mx[m 选择/随机签名档 [1;32mt[m标题，[1;32mu[m回复，[1;32mq[m放弃:'
    
#     def update_attr(self, attrs):
#         self.write(''.join([ac.move2(21,1),
#                             ac.clear1,
#                             self.render_str('edit_head', **attrs)]))

#     def read_attrs(self):
#         sign_num = manager.usersign.get_sign_num(self.userid)
#         attrs = {
#             "boardname":self.boardname,
#             "replyable":True,
#             "usesign":0,
#             "title":self.title,
#             }
#         if sign_num :
#             attrs['usesign'] = random.randint(1, sign_num)
#         self.update_attr(attrs)
#         prompt = ''.join([ac.move2(25,1), ac.kill_line, self.prompt % sign_num])
#         while True:
#             op = self.readline_safe(buf_size=4, prompt=prompt)
#             if op == '':
#                 break
#             elif op is False or op=='q':
#                 return None
#             elif op == 't' :
#                 attrs['title'] = self.readline_safe(prompt=u'\r\x1b[K请输入标题：',
#                                                     prefix=attrs['title'],buf_size=40)
#                 if not attrs['title'] :
#                     return
#             elif op == 'u' :
#                 attrs['replyable'] = not attrs['replyable']
#             elif op == 'x' and sign_num:
#                 attrs['usesign'] = random.randint(1, sign_num)
#             elif op.isdigit() :
#                 n = int(op)
#                 if n <= sign_num :
#                     attrs['usesign'] = n
#             self.update_attr(attrs)
#         return attrs

#     # @need_perm
#     def initialize(self, boardname, post):
#         self.cls()
#         self.boardname = boardname
#         self.replyid = post['pid']
#         self.title = post['title'] if post['title'].startswith('Re:')\
#             else 'Re: %s' % post['title']
#         self.attrs = self.read_attrs()
#         if not self.attrs :
#             self.goto_back()
#         self.title = self.attrs['title']
#         self.signtext = manager.usersign.get_sign(self.userid, self.attrs['usesign']-1) \
#             if self.attrs['usesign'] else ''
#         text = gen_quote(post)
#         super(ReplyPostFrame, self).initialize(text=style_to_etelnet(text))
#         self.message(u'回复文章 -- %s' % self.title)

#     def finish(self):
#         text = etelnet_to_style(self.fetch_all())
#         pid = manager.action.reply_post(
#             self.boardname,
#             self.userid,
#             self.title,
#             text,
#             self.session.ip,
#             config.BBS_HOST_FULLNAME,
#             self.replyid,
#             replyable=True,
#             signature=self.signtext)
#         board = manager.board.get_board(self.boardname)
#         index = manager.post.get_rank_num(self.boardname, pid)
#         invs = find_all_invert(text)
#         if len(invs) >= 10:
#             self.message(u'你@太多人啦！')
#             self.pause()
#         else:
#             userids = []
#             for u in invs :
#                 user = manager.userinfo.get_user(u)
#                 if user :
#                     userids.append(user['userid'])
#             manager.notice.add_inve(self.userid, self.boardname,
#                                     pid, userids)
#             for u in userids:
#                 manager.notify.add_notice_notify(u)
#         self.goto('board', board=board, default=index)

# @mark('edit_post')
# class EditPostFrame(BaseEditFrame):

#     def check_perm(self, board, post):
#         # _,w,_,_ = manager.query.get_board_ability(self.session.user.userid, board['boardname'])
#         # return (w or u'该版禁止发文或你没有相应的权限！') and
#         return (post.owner == self.userid) or u'你没有编辑此文章的权限！'

#     @need_perm
#     def initialize(self, board, post):
#         self.cls()
#         self.boardname = board['boardname']
#         self.pid = post['pid']
#         super(EditPostFrame, self).initialize(text=post['content'])
#         self.message(u'开始编辑文章')
        
#     def finish(self):
#         manager.action.update_post(self.boardname,
#                                    self.userid,
#                                    self.pid,
#                                    etelnet_to_style(self.fetch_all()))
#         # self.message(u'编辑文章成功！')
#         # self.pause()
#         self.goto_back()

# @mark('edit_text')
# class EditFileFrame(BaseEditFrame):

#     def initialize(self, filename, callback, text='', l=0, split=False):
#         self.cls()
#         self.filename = filename
#         self.split = split
#         self.callback = callback
#         super(EditFileFrame, self).initialize(text=text, spoint=l)
#         self.message(u'开始编辑档案')

#     def finish(self):
#         self.message(u'修改档案结束!')
#         if self.split:
#             self.callback(filename=self.filename, text=self.fetch_lines())
#         else:
#             self.callback(filename=self.filename, text=self.fetch_all())
#         # self.pause()
#         self.goto_back()

#     def quit_iter(self):
#         self.message(u'放弃本次编辑操作？')
#         d = self.readline()
#         if not d :
#             self.goto_back()

# @mark('edit_clipboard')
# class EditorClipboardFrame(BaseEditFrame):

#     def initialize(self):
#         super(EditorClipboardFrame, self).initialize(text=self.get_text())

#     def finish(self):
#         manager.clipboard.set_clipboard(self.userid, self.fetch_all())
#         self.message(u'更新暂存档成功！')
#         # self.pause()
#         self.goto_back()

#     def get_text(self):
#         return self.u(manager.clipboard.get_clipboard(self.userid))
