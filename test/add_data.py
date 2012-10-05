
import MySQLdb

DATA_LIMIT = 1000000

def add_data(cursor, content):
    num = 0
    while num < DATA_LIMIT:
        num += 1
        user = 'hbl-%d' % (num % 10000)
        title = 'title-%d' % (num % 12345)
        bid = num % 200
        cursor.execute("insert into argo_pindex(bid, owner, title, content)\
                values(%s, %s, %s, %s)", (bid, user, title, content))
        if num % 1000 == 0:
            print num

def main():
    conn = MySQLdb.Connection(user='argo', passwd='forargo', db='argo')
    conn.autocommit(True)
    cursor = conn.cursor()
    content = file('model_test.py').read()
    add_data(cursor, content)

if __name__ == '__main__':
    main()

