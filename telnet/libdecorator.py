#!/usr/bin/python2
# -*- coding: utf-8 -*-

from model import manager
from functools import wraps

def need_perm(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        p = self.check_perm(*args, **kwargs)
        if p is True:
            return f(self, *args, **kwargs)
        else:
            self.writeln(p)
            self.pause()
            self.goto_back()
    return wrapper

def need_perm_checker(checker):
    def inner(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            p = checker(self, *args, **kwargs)
            if p is True:
                return f(self, *args, **kwargs)
            else:
                self.writeln(p)
                self.pause()
                self.goto_back()
        return wrapper
    return inner

# def need_board_read_perm(f):
#     @wraps(f)
#     def wrapper(self, board):
#         r,_,_,_ = manager.get_board_ability(self.session.user.userid, board['boardname'])
#         if not r :
#             self.authed = False
#             self.writeln(u'错误的讨论区或你无权力进入该版')
#             self.pause()
#             self.goto_back()
#         self.authed = True
#         return f(self,board)
#     return wrapper

# def need_board_post_perm(f):
#     @wraps(f)
#     def wrapper(self, board, *args, **kwargs):
#         _,w,_,_ = manager.get_board_ability(self.session.user.userid, board['boardname'])
#         if not w :
#             self.cls()
#             self.writeln(u'该版禁止发文或你没有相应的权限！')
#             self.authed = False
#             self.pause()
#             self.goto_back()
#         self.authed = True
#         return f(self,board, *args, **kwargs)
#     return wrapper

# def need_board_reply_perm(f):
#     @wraps(f)
#     def wrapper(self, board, *args, **kwargs):
#         _,w,_,_ = manager.get_board_ability(self.session.user.userid, board['boardname'])
#         if not w :
#             self.cls()
#             self.writeln(u'该版禁止发文或你没有相应的权限！')
#             self.authed = False
#             self.pause()
#             self.goto_back()
#         self.authed = True
#         return f(self,board, *args, **kwargs)
#     return wrapper

# def need_board_edit_perm(f):
#     @wraps(f)
#     def wrapper(self, board, *args, **kwargs):
#         _,w,_,_ = manager.get_board_ability(self.session.user.userid, board['boardname'])
#         if not w :
#             self.cls()
#             self.writeln(u'该版禁止发文或你没有相应的权限！')
#             self.authed = False
#             self.pause()
#             self.goto_back()
#         self.authed = True
#         return f(self,board, *args, **kwargs)
#     return wrapper
