#!/usr/bin/python2
# -*- coding: utf-8 -*-

from lib import BaseHandler, manager

class IndexHandler(BaseHandler):

    def get(self):
        billboard = manager.web.get_billboard()
        topten = manager.web.get_topten()
        boardnav = manager.web.get_board_nav()
        news = manager.web.get_news()
        self.srender("index.html", billboard=billboard,
                     topten=topten, boardnav=boardnav,
                     news=news)

class LoginHandler(BaseHandler):

    def post(self):
        try:
            userid = manager.auth.login_http(
                self.get_argument("userid"),
                self.get_argument("passwd"),
                self.request.remote_ip,
                )
        except Exception as e:
            self.write(e.message)
            self.finish()
        else:
            print repr(userid)
            self.set_secure_cookie('userid', userid)
        self.redirect('/')

class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie('userid')
        self.redirect('/')
