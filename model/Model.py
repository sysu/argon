import dbapi
from globaldb import global_conn

class Model(object):

    def __init__(self):
        self.db = global_conn;

    def query(self, sql):
        res = self.db.query(sql)
        print 'DEBUG: sql %s %d' % (sql,len(res))
        return res

    def escape_string(self, rawsql):
        safe_sql = self.db.escape_string(rawsql)
        return safe_sql

    def execute(self, sql):
        self.db.execute(sql)

    def toStr(sql, s):
        return "'"+str(s)+"'";

    def gen_update(self, kv, ignore_keys):
        """
            Generate update setting experssion for sql :
                attr1=value1, attr2=value2, attr3=value3 ...
            TODO: escape string
        """
        key_value = [ str(key)+'='+str(val) for key,val in kv  if key not in ignore_keys]
        return key_value

    def close():
        self.db.close()


