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

p = Post()
p.bid = b.bid
for i in range(10):
    p.owner = 'ggggggg' + str(i)
    p.content = 'ccccccc...';
    b.add_post(p)

posts = b.get_last(20)
for post in posts:
    print post.__dict__

print b.get_total()

#p = Post()
#p.bid = b.bid;
#p.owner = 'gcc'
#
#for i in range(0, 10):
#    p.content = str(i)
#    b.add_post(p)
#
# select them out


# check if insert is ok


# close it
b.close()


