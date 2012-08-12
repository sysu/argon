#!/usr/bin/env python

from model import manager as mgr
import threading,random,os,time
#for i in xrange(100000):
#   mgr.action.new_post(boardname = 'Test',\
#           userid = 'test',\
#           title = 'title %s' % i,\
#           content = 'content %s' % i,\
#           addr = '127.0.0.1',\
#           host = 'TestLand') 
#   print i
#

process_num =  1

lastpid = mgr.post.get_last_pid('Test')

def random_select():
    
    for i in xrange(100000):
        if i % 100: print i
        pid = random.randint(1, lastpid)
        res = mgr.post.get_posts('Test', pid, 25)


old = time.time()
random_select()
print time.time() - old

