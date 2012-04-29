#!/usr/bin/env python

from model import Board
from model import Post

"""
    Uint test for Board
"""

# create a board instance
b = Board('Test')

# batch insert several posts into baord
b.get_total()

""" Test add post """

p = Post()
p.bid = b.bid
for i in range(6):
    p.owner = 'ggggggg' + str(i)
    p.content = 'ccccccc...';
    b.add_post(p)

"""  get last """
posts = b.get_last(5)
print "get_last: %d" % len(posts)

""" update_post """
for p in posts:
    p.owner += ' new ccc'
    p.content += ' defgh'
    b.update_post(p)

""" get total """
print b.get_total()


""" del post """
print "Before Delete: %d" % b.get_total()
b.del_last(5)
print "After delete: %d" % b.get_total()


# close it
b.close()


