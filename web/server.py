#!/usr/bin/env python

import sys
sys.path.append('..')
import os
import tornado
import tornado.ioloop
import tornado.web
import tornado.httpserver
from model import globaldb
from comm.urls import urls

class Application(tornado.web.Application):

    def __init__(self):
        handlers = urls 
        settings = dict (
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        )
        tornado.web.Application.__init__(self, handlers, **settings)
    
        # set db and cache here
        self.db = globaldb.global_conn
        self.ch = globaldb.global_cache


def main():
    application = Application()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    
    main() 


