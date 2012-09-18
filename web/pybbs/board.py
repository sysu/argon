#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('..')

import tornado.web
from model import manager as mgr
from comm.urls import mark,BaseHandler
from base import *
from comm.funcs import *

@mark('PBoardHandler')
class PBoardHandler(PBaseHandler):

    def get(self):
        self.mrender('board.html')

