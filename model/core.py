class MetaModel(type):

    all_model = []

    def __new__(cls,names,bases,attrs):
        old_cls = cls
        cls = super(MetaModel,cls).__new__(cls,names,bases,attrs)
        if attrs.get('__clsinit__') is not None:
            cls.__clsinit__(names,bases,attrs,old_cls)
        cls.__modelname__ = names
        old_cls.all_model.append(cls)
        return cls

class Model:
    
    u'''
    A base class for a model. It implemented some common methods as well.
    Basic useage read the Manage class.
    '''
    
    __metaclass__ = MetaModel

    def __init__(self):
        self.dict = {}
    
    def bind(self,db=None,ch=None):
        if db : self.db = db
        if ch : self.ch = ch

    def configure(self):
        pass

    def table_select_all(self,tablename):
        return self.db.query("SELECT * FROM `%s`" % tablename)

    def table_get_by_key(self,tablename,key,value):
        return self.db.get("SELECT * FROM `%s` WHERE %s = %%s" %\
                               (tablename,key),
                           value)

    def execute_paragraph(self, para):
        self.db.execute_paragraph(para)

    def table_insert(self,tablename,attr):
        names,values = zip(*attr.items())
        cols = ','.join(map(str,names))
        vals = ','.join(('%s',) * len(values))
        return self.db.execute("INSERT INTO `%s` (%s) VALUES (%s)" % \
                                   (tablename, cols,vals),
                               *values)
    
    def table_update_by_key(self,tablename,key,value,attr):
        names,values = zip(*attr.items())
        set_sql = ','.join( map(lambda x: "%s = %%s" % x,names))
        return self.db.execute("UPDATE `%s` SET %s WHERE %s = %%s" % \
                                   (tablename, set_sql, key),
                               *(values + (value,)))

    def table_delete_by_key(self,tablename,key,value):
        return self.db.execute("DELETE FROM `%s` WHERE %s = %%s" % \
                                   (tablename, key),
                               value)

    def table_select_by_key(self,tablename,what,key,value):
        return self.db.get("SELECT %s FROM `%s` WHERE %s = %%s" %\
                               (what, tablename, key),
                           value)

    def table_get_listattr(self, tablename, what, key, value):
        res = self.db.get("SELECT %s FROM `%s` WHERE %s=%%s"%(what, tablename, key),
                          value)
        return res and ( (res[what] and res[what].split(':')) or [])

    def table_update_listattr(self, tablename, what, listattr, key, value):
        r = ':'.join(listattr)
        return self.db.execute("UPDATE `%s` SET %s=%%s WHERE %s=%%s" % \
                                   (tablename, what, key),
                               r, value)

def with_index(d):
    for index in range(len(d)):
        d[index]['rownum'] = index
    return d

def add_column(coldef,after,*tables):
    for table in tables:
        try:
            global_conn.execute("ALTER TABLE `%s` "
                                "ADD COLUMN %s AFTER `%s`" %\
                                    (table, coldef, after))
        except Exception as e:
            print e.message

def update_all(setsql, *tables):
    for table in tables:
        global_conn.execute("UPDATE `%s` "
                            "SET %s" % (table, setsql))

def sql_all_boards(sql):
    d = Board()
    d.bind(global_conn)
    for table in map(lambda x : 'argo_filehead_%s' % x['boardname'],
                     d.get_all_boards()):
        try:
            global_conn.execute(sql % table)
        except Exception as e:
            print '[FAIL] %s' % e.message
        else:
            print '[SUCC] %s' % (sql % table)

def foreach_board(f):
    d = Board()
    d.bind(global_conn)
    for board in d.get_all_boards():
        f(board)
