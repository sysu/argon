#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
from lib import BaseHandler, manager

class BoardHandler(BaseHandler):

    page_size = 30

    def get(self, boardname, rank=None):
        board = manager.board.get_board(boardname)
        if not board:
            raise tornado.web.HTTPError(404)
        boardname = board.boardname
        maxrank = max(0, manager.post.get_post_total(board['bid']))
        if rank is None:
            rank = maxrank // self.page_size * self.page_size
        else :
            rank = int(rank)
        posts = manager.post.get_posts(board['bid'], rank, self.page_size)
        if self.get_current_user() :
            userid = self.get_current_user()
            manager.readmark.wrapper_post_with_readmark(posts, boardname, userid)
            isfav = manager.favourite.is_fav(userid, board.bid)
        else:
            isfav = None            
        vistors = (
            ("LTaoist", "2012-03-04"),
            ("gcc", "2012-01-09"),
            ("cypress", "2012-01-01"),
            )
        board['bm'] = board['bm'] and board['bm'].split(':')
        board['httpbg'] = "http://ww3.sinaimg.cn/large/6b888227jw1dwesulldlyj.jpg"
        self.srender('board.html', board=board, rank=rank, maxrank=maxrank,
                     posts=posts, vistors=vistors, isfav=isfav,
                     page_size=self.page_size)

class AjaxBookBoardHandler(BaseHandler):

    def get(self, boardname):
        userid = self.get_current_user()
        if userid is None:
            self.write({
                    "success": False,
                    "content": u"未登录用户.",
                    })
            return
        board = manager.board.get_board(boardname)
        if not board :
            self.write({
                    "success": False,
                    "content": u"没有该版块."
                    })
            return
        manager.favourite.add(userid, board.bid)
        return self.write({
                "success": True,
                "content": u"预定成功！",
                })
