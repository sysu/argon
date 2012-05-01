#!/usr/bin/env python
from model.Model import Model,Board,Post, User
from model.globaldb import global_conn
import sys

"""
    Uint test for user
"""

u = User('sysop')

class TestSuit(object):

    def check_mail(self):
        newmails = u.check_mail()
        print 'unread mail: %d' % newmails

    def usage(self):
        print """
        usage > python testboard.py
                    check_mail
        """


t = TestSuit()
if len(sys.argv) < 2: t.usage()
else: getattr(t, sys.argv[1])()




