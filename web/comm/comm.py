#!/usr/bin/env python

import tornado.web
from urls import mark,BaseHandler

@mark('HomeHandler')
class HomeHandler(BaseHandler):
    
    def get(self):
        self.write('Welcome!')



