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
        print 'DEBUG: Connect %s@%s:%d pwd=%s db=%s' % (self.user,self.host,self.port,self.passwd, self.dbname)

    def query(self, sql):
        res = self.cursor.execute(sql)
        self.conn.commit()
        print 'DEBUG: sql %s %d' % (sql,res)
        return res

    def escape_string(self, rawsql):
        safe_sql = MySQLdb.escape_string(rawsql)
        return safe_sql

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def gen_update(self, kv, ignore_keys):
        """
            Generate update setting experssion for sql :
                attr1=value1, attr2=value2, attr3=value3 ...
            TODO: escape string
        """
        key_value = [ str(key)+'='+str(val) for key,val in kv  if key not in ignore_keys]
        return key_value

    def closedb(self):
        if hasattr(self, 'conn'):
            self.conn.close()

