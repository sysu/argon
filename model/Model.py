<<<<<<< HEAD
from config import *
=======
import MySQLdb
import config
>>>>>>> eca48b9444efad48ab40d2ead20cb0f4f37a5dbe

class Model(object):

    def __init__(self, cfg = dbConfig()):
        self.host = cfg.host
        self.port = cfg.port
        self.user = cfg.user
        self.passwd = cfg.passwd
        self.dbname = cfg.dbname

    def connect(self):
<<<<<<< HEAD
        self.conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd,db=self.dbname)
        self.cursor = self.conn.cursor()
        print "Connect %s@%s:%d pwd=%s db=%s" % (self.user,self.host,self.port,self.passwd, self.dbname)
=======
        try:
            self.conn = MySQLdb.connect(self.host, self.port, self.user, self.passwd, self.db)
            self.cursor = self.conn.cursor()
        except:
            ## will write to log later
            print "ERR: connect %s:%d %s:%s %s" % self.host, self.port, self.user, self.passwd, self.db
>>>>>>> eca48b9444efad48ab40d2ead20cb0f4f37a5dbe

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
<<<<<<< HEAD
        if hasattr(self, "conn"):
            self.conn.close()
=======
        self.conn.close()
>>>>>>> eca48b9444efad48ab40d2ead20cb0f4f37a5dbe

