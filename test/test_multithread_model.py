import sys
sys.path.append('..')

import threading
import eventlet
from eventlet import greenthread
from model import manager as mgr

def segment_fetch(boardname, start_num, end_num):

    print start_num, end_num
    for i in xrange(start_num, end_num):
        r = mgr.post.get_post(boardname, i)
        if i % 1000 == 0:
            print threading.current_thread(), i

    print 'finish seg %d %d' % (start_num, end_num)

def press_test(thread_num):

    boardname = 'Test'
    lastpid = mgr.post.get_last_pid(boardname)
    seg_num = lastpid // thread_num
    threads = []
    pool = eventlet.GreenPool(thread_num)
    for i in xrange(thread_num):
        th = pool.spawn_n(segment_fetch, boardname=boardname, start_num=seg_num*i, end_num=seg_num*i+seg_num)
        #print dir(th)
        #th.run(boardname, seg_num*i, seg_num*i+seg_num)
        #th.start()
        #threads.append(th)

    #for th in threads:
    #    th.join()

    print 'finish test'
    pool.waitall()


if __name__ == '__main__':
    press_test(thread_num = 4)



