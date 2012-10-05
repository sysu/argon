import MySQLdb,time


def post_list_test(cursor):
    '''
    index+content : 2 s
    all: 7~8s
    '''
    old = time.time()
    for bid in range(0, 200):
        for page in xrange(120,140):
            cursor.execute('select * from argo_pindex where bid = %s order by pid desc limit \
                %s,25', (bid, page))
            res = cursor.fetchall()
            #print res[0][0]
    diff = time.time() - old;
    print diff

def post_test(cursor):
    pid_arr = []
    for bid in range(0, 200):
        for page in xrange(120,140):
            cursor.execute('select pid from argo_index where bid = %s order by pid desc limit \
                %s,25', (bid, page))
            res = cursor.fetchall()
            pid_arr += [r[0] for r in res]
    print len(pid_arr)
    old = time.time()
    cnt = 0
    for pid in pid_arr:
        cnt += 1
        cursor.execute('select * from argo_content where pid = %s', pid)
        res = cursor.fetchall()
        if cnt % 1000 == 0: print cnt
    diff = time.time() - old
    print 'done %s , %s ms/query' % (diff, (diff*1000)/len(pid_arr)) 

def main():
    conn = MySQLdb.Connection(user='argo', passwd='forargo', db='argo')
    conn.autocommit(True)
    cursor = conn.cursor()
    post_list_test(cursor)
    #post_test(cursor)

if __name__ == '__main__':
    main()

