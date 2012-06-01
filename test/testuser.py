#!/usr/bin/env python
from model.Model import Model,Board,Post, User
from model.globaldb import global_conn
import sys

"""
    Uint test for user
"""

u = User('gcc')

class TestSuit(object):

    def check_mail(self):
        newmails = u.check_mail()
        print 'unread mail: %d' % newmails

    def usage(self):
        print '\r\n'.join(filter(lambda x : not x.endswith('__'),dir(self)))



t = TestSuit()
if len(sys.argv) < 2: t.usage()
else: getattr(t, sys.argv[1])(*sys.argv[2:])




