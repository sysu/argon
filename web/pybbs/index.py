#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('..')

import tornado.web
from model import manager as mgr
from comm.urls import mark,BaseHandler
from base import *
from comm.funcs import *

@mark('PIndexHandler')
class PIndexHandler(PBaseHandler):

    def get(self):
        self.mrender('index.html')


