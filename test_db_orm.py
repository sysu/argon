#!/usr/bin/env python

from model.Model import db_orm

import sys

"""
    Uint test for db_orm
"""

class TestSuit(object):

    def add_section(self):
        db_orm.add_section('Test',{"description":"Section for test."})

    def get_section(self):
        s = db_orm.get_section('Test')
        print s
        print s.dump_attr()
        print s.get_allboards()

    def add_board(self):
        db_orm.add_board('Test',{"description":"Board for test.","sid":1})

    def get_board(self):
        b = db_orm.get_board('Test')
        print b.dump_attr()

    def add_user(self):
        u = db_orm.add_user('Jia','2022',{"email":"no@e.com"})

    def get_user(self):
        u = db_orm.get_user('Jia')
        print u.dump_attr()

    def usage(self):
        print '\r\n'.join(filter(lambda x : not x.endswith('__'),dir(self)))

t = TestSuit()
if len(sys.argv) < 2: t.usage()
else: getattr(t, sys.argv[1])()
