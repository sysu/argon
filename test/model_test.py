#!/usr/env python

import sys
sys.path.append('..')

from model import manager as mgr

class TestSuit(object):

    def usage(self):
        print """ python model_test.py  <function name> <*argv> """

    ############  Post ################

    def new_post(self):
        for i in xrange(20):
            if i % 2: boardname = 'Test'
            else: boardname = 'water'
            mgr.action.new_post(boardname, 'hbl-%s' % i, 'title-%s' % i, 'content-%s' % i,
            'addr-%s' % i, 'host-%s' % i, 1, 'signature-%s' % i )
            print i

    def get_posts(self, bid, start, limit):
        start,limit = int(start), int(limit)
        rows = mgr.post.get_posts(bid, start, limit)
        for r in rows:
            print r.pid

    def get_posts_total(self, bid):
        print mgr.post.get_posts_total(bid)

    def get_posts_g(self, bid, start, limit):
        start,limit = int(start), int(limit)
        rows = mgr.post.get_posts_g(bid, start, limit)
        for r in rows:
            print r.pid

    def get_posts_g_total(self, bid):
        print mgr.post.get_posts_g_total(bid)

    def get_posts_m(self, bid, start, limit):
        start,limit = int(start), int(limit)
        rows = mgr.post.get_posts_m(bid, start, limit)
        for r in rows:
            print r.pid

    def get_posts_m_total(self, bid):
        print mgr.post.get_posts_m_total(bid)

    def get_posts_topic(self, bid, start, limit):
        start,limit = int(start), int(limit)
        rows = mgr.post.get_posts_topic(bid, start, limit)
        for r in rows:
            print r.pid

    def get_posts_onetopic(self, tid, bid, start, limit):
        start,limit = int(start), int(limit)
        rows = mgr.post.get_posts_onetopic(tid, bid, start, limit)
        for r in rows:
            print r.pid

    def get_posts_onetopic_total(self, tid, bid):
        print mgr.post.get_posts_onetopic_total(tid, bid)

    def get_post(self, pid):
        row = mgr.post.get_post( pid)
        print row.pid, row.content

    def prev_post(self, bid, pid):
        row = mgr.post.prev_post(bid, pid)
        print row.pid,row.content

    def next_post(self, bid, pid):
        row = mgr.post.next_post(bid, pid)
        print row.pid,row.content

    def remove_post_junk(self, bid, pid):
        mgr.post.remove_post_junk(bid, pid)
    
    #######  mail ############# 

    def send_mail(self, fromuserid, touserid):
        for i in xrange(20):
            content = 'content-%s' % i
            quote = 'quote-%s' % i
            mgr.action.send_mail(fromuserid, touserid, content = content, quote = quote)
    
    def one_mail(self, mid):
        print mgr.action.one_mail(mid)
    
    def reply_mail(self, userid, mid, content):
        mail = mgr.action.one_mail(mid)
        mgr.action.reply_mail(userid, mail, content = content)

    ######  User #############
    def register(self, userid, passwd):
        print mgr.auth.register(userid, passwd)

def main():
    t = TestSuit()
    if len(sys.argv) < 2: t.usage()
    else:
        getattr(t, sys.argv[1])(*sys.argv[2:])

if __name__ == '__main__':
    main()

