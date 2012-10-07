#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')
import os
import tornado
import tornado.ioloop
import tornado.web
import tornado.httpserver
from model import globaldb
from lib import import_handler
import uimodules

class Application(tornado.web.Application):

    def __init__(self, handlers, **settings):
        tornado.web.Application.__init__(self, handlers, **settings)
        # set db and cache here
        self.db = globaldb.global_conn
        self.ch = globaldb.global_cache

urls = [
    (r"/", import_handler("index", "IndexHandler")),
    (r"/account/login", import_handler("index", "LoginHandler")),
    (r'/account/logout', import_handler('index', 'LogoutHandler')),
    (r'/board/(\w{1,40})/(\d{1,10})?', import_handler('board', 'BoardHandler'))
    # (r"/post/(\d{1,10})", import_handler("post", "PostHandler")),
    # (r"(
    ]

settings = dict (
    template_path=os.path.join(os.path.dirname(__file__), "template"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    # xsrf_cookies=True,
    cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    autoescape='xhtml_escape',
    ui_modules=uimodules,
    debug=True,
    )

def main():
    application = Application(urls, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
