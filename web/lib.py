#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
   argon.web.lib
   ~~~~~~~~~~~~~

   Some common function and base.

'''

from model import manager
from datetime import datetime
import tornado

class SDict(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        return self[name]

def url_for_avatar(userid):
    '''
    Return the avatar url for userid.
    NOT IMPLEMENTED YET.
    '''
    return "/static/img/avatar/%s" % userid

func = SDict([
    ("url_for_avatar", url_for_avatar),
    ])

class BaseHandler(tornado.web.RequestHandler):

    '''The BaseHandler for all handler.'''

    @property
    def db(self):
        return self.application.db

    @property
    def ch(self):
        return self.application.ch

    @property
    def headers(self):
        return self.application.headers

    def get_current_user(self):
        return self.get_secure_cookie('userid')

    def srender(self, tpl, **kwargs):
        '''Wrap func into template namespace.'''
        return self.render(tpl, func=func, **kwargs)

def import_handler(modulename, classname):
    '''
    Import a class from the module, and return it.
    It common use to setting the urls in server.py.
    '''
    module = __import__(name=modulename, fromlist=classname, level=0)
    return getattr(module, classname)

def bid_wrapper(userid):
    '''
    Wrapper the bid as a board object, with the read status of userid.
    '''
    def wrapper(bid):
        board = manager.board.get_board_by_id(bid)
        board['is_new'] = manager.readmark.is_new_board(userid, bid,
                                                        board.boardname)
        return board
    return wrapper

def timeformat(time):
    '''
    Better outlook for time.
    '''
    return time.strftime("%d-%m")


def fun_gen_quote(userid, content):
    '''
    Wrapper the content by userid to be quote.
    '''    
    max_quote_line = 5

    owner = mgr.userinfo.get_user(userid)
    if not owner: owner['userid'] = owner['nickname'] = 'null' 

    pattern = u'【 在 %s ( %s ) 的大作中提到: 】' % \
                ( owner['userid'], owner['nickname'] )

    quote = pattern + '\n' + '\n'.join(map(lambda l: u'：'+l, content.split('\n')[:max_quote_line]))

    return quote

