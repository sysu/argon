from config import *

class Model(object):

    def __init__(self, cfg = dbConfig()):
        self.host = cfg.host
        self.port = cfg.port
        self.user = cfg.user
        self.passwd = cfg.passwd
        self.dbname = cfg.dbname

    def connect(self):
        self.conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd,db=self.dbname)
        self.cursor = self.conn.cursor()
        print "Connect %s@%s:%d pwd=%s db=%s" % (self.user,self.host,self.port,self.passwd, self.dbname)

    def query(self, sql):
        self.cursor.execute(sql)

    def escape_string(self, rawsql):
        safe_sql = MySQLdb.escape_string(rawsql)
        return safe_sql

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def closedb(self):
        if hasattr(self, "conn"):
            self.conn.close()

