#!/usr/bin/env python

from model import Board
from model import Post
import sys

"""
    Uint test for Board
"""

# create a board instance
b = Board('Test')

class TestSuit(object):

    """ get total """
    def get_total(self):
        print b.get_total()

    """ Test add post """
    def add_post(self):
        p = Post()
        p.bid = b.bid
        for i in range(5):
            p.owner = 'ggggggg' + str(i)
            p.content = 'ccccccc...';
            b.add_post(p)

    """ del last """
    def del_last(self):
        b.del_last(10)

    """ update_post """
    def update_post(self):
        posts = b.get_last(10)
        for p in posts:
            p.owner = ' new ccc'
            p.content += ' more more' + str(p.pid)
            b.update_post(p)

    """ del post """
    def del_last(self):
        print "Before Delete: %d" % b.get_total()
        b.del_last(5)
        print "After delete: %d" % b.get_total()

    """ Test db connectio """
    def board_db(self):
        barr = []
        for i in range(10):
            barr.append(Board('Test'))

    def usage(self):
        print """
        usage > python testboard.py { get_total | add_post | del_last | update_post | board_db}
        """


t = TestSuit()
if len(sys.argv) < 2: t.usage()
else: getattr(t, sys.argv[1])()




