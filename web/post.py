#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
from lib import BaseHandler, manager, fun_gen_quote

class PostHandler(BaseHandler):

    def get(self, pid):
        post = manager.post.get_post(pid)
        if not post:
            raise tornado.web.HTTPError(404)
        board = manager.board.get_board_by_id(post['bid'])
        if post.replyid :
            parent = manager.post.get_post(post.replyid)
            root = manager.post.get_post(post.tid)
            firstpid = root.pid
        else:
            parent = root = None
            firstpid = post.pid
        children = manager.post.get_post_by_replyid(post.pid)
        prevpid = manager.post.prev_post_pid(post.bid, post.pid)
        nextpid = manager.post.next_post_pid(post.bid, post.pid)
        lastpid = manager.post.get_topice_last_pid(post.tid)
        if self.get_current_user() :
            userid = self.get_current_user()
            manager.readmark.set_read(userid, board.boardname, pid)
        self.srender('post.html', board=board, post=post,
                     parent=parent, root=root, children=children,
                     firstpid=firstpid, prevpid=prevpid,
                     nextpid=nextpid, lastpid=lastpid)

class ReplyPostHandler(BaseHandler):

    def get(self, replyid):
        post = manager.post.get_post(replyid)
        if post is None:
            raise tornado.web.HTTPError(404)
        if not self.get_current_user():
            raise tornado.web.HTTPError(404)
        default = fun_gen_quote(post.owner, post.content)
        title = post.title if post.title.startswith('Re:') \
            else 'Re: %s' % post.title
        self.srender("replypost.html", post=post, title=title,
                     default=default)

    def post(self, replyid):
        userid = self.get_current_user()
        if not userid :
            raise tornado.web.HTTPError(404)
        post = manager.post.get_post(replyid)
        boardname = manager.board.id2name(post.bid)
        signnum = self.get_argument('signnum', None)
        if signnum is None or signnum < manager.usersign.get_sign_num(userid):
            signature = ''
        else:
            signature = manager.usersign.get_sign(userid, signnum)
        pid = manager.post.add_post(
            owner=userid, title=self.get_argument('title'),
            bid=post.bid, content=self.get_argument('content'),
            replyid=replyid, fromaddr=self.request.remote_ip,
            tid=post.tid, replyable=(self.get_argument('replyable')=='on'),
            signature=signature)
        manager.readmark.set_read(userid, boardname, pid)
        self.redirect('/post/%s' % pid)
        #################### HERE

class NewPostHandler(BaseHandler):

    def get(self, boardname):
        self.render('newpost.html')

    def post(self, boardname):
        userid = self.get_current_user()
        if not userid:
            raise tornado.web.HTTPError(404)
        bid = manager.board.name2id(boardname)
        boardname = manager.board.name2id(bid)
        signnum = self.get_argument('signnum', None)
        if signnum is None or signnum < manager.usersign.get_sign_num(userid):
            signature = ''
        else:
            signature = manager.usersign.get_sign(userid, signnum)
        pid = manager.post.add_post(
            bid=bid, owner=userid, title=self.get_argument('title'),
            content=self.get_argument('content'), replyid=0,
            fromaddr=self.request.remote_ip,
            replyable=(self.get_argument('replyable')=='on'),
            signature=signature)
        manager.post.update_post(pid, tid=pid)
        manager.readmark.set_read(userid, boardname, pid)
        self.redirect('/post/%s' % pid)
