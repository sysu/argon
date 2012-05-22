__metaclass__ = type

from globaldb import global_conn
from globaldb import global_cache

class MetaModel(type):

    def __new__(cls,names,bases,attrs):
        cls = super(MetaModel,cls).__new__(cls,names,bases,attrs)
        if attrs.get('__clsinit__') :
            cls.__clsinit__(names,bases,attrs)
        return cls

class Model:

    __metaclass__ = MetaModel

    db = global_conn
    ch = global_cache
    
    #######################
    # for record in table #
    #######################
    
    def __init__(self,**attr):
        self.dict = attr
        
    def __getitem__(self,key):
        return self.dict.get(key)
            
    def __setitem__(self,key,value):
        self.dict[key] = value

    def dump_attr(self):
        return self.dict

    def dump_attr_safe(self):
        return self.dict.copy()
    
    def __str__(self):
        return "<%s>{%s}" % (self.__class__.__name__,
                             nice_dict(lambda k,w : "'%s':'%s' " % (k,w),
                                       self.dump_attr(),','))

    ##############################
    # base for orm               #
    ##############################

    @classmethod
    def __clsinit__(cls,names,bases,attrs):
        pass

    @classmethod
    def escape_string(cls,rowsql):
        return cls.db.escape_string(rowsql)

    @classmethod
    def wrap_up(cls,res):
        return [ cls(**x) for x in res]

class TableModel(Model):

    __ = 'tablename'

    @classmethod
    def get_all_nw(cls):
        return cls.db.query("SELECT * FROM %s" % cls.__)

    @classmethod
    def get_all(cls):
        return cls.wrap_up(cls.get_all_nw())

    @classmethod
    def insert_dict(cls,tablename,dic):
        ''' Change to INSERT INTO tablename (col1,col2,col3..) VALUES (%s,%s,%s...),
        and auto escape string. '''
        names,values = zip(*dic.items())
        sql = "INSERT INTO %s (%s) VALUES (%s)" % \
            (tablename, ','.join(names) , ','.join(['%s'] * len(values)))
        return cls.db.execute(sql,*values)
    
class IdModel(TableModel):

    __idname__ = 'id'
    __ = None
    
    @property
    def id(self):
        return self.dict[self.__idname__]

    def save(self):
        self[self.__idname__] = self.insert_dict(self.__,self.dump_attr())
        self.fetch()

    def update(self):
        self[self.__idname__] = self.db.execute(
            "UPDATE %s SET %s WHERE %s = %%s" %\
                (self.__, sql_update_set(self.dict),
                 self.__idname__) ,
            self.id)

    def delete(self):
        return self.db.execute("DELETE FROM %s WHERE %s = %%s" % \
                                   ( self.__, self.__idname__ ),
                               self.id)

    def fetch(self):
        res = self.get_nw(self.id)
        self.dict = res

    @classmethod
    def get_nw(cls, _id):
        return cls.db.execute("SELECT * FROM %s WHERE %s = %%s" %\
                                   ( cls.__, cls.__idname__),
                               _id)

    @classmethod
    def get(cls, _id):
        return cls(**cls.one_nw(_id))

def nice_dict(lbd_format,dic,seq=' '):
    buf = map(lambda x : lbd_format(*x),dic.items())
    return seq.join(buf)

def sql_str(data):
    return "'%s'" % data

def sql_insert(tablename, kwargs):
    from MySQLdb import escape_string
    names,values = zip(*kwargs.items())
    return test_print(escape_string("INSERT INTO %s (%s) VALUES (%s)" % \
                              (tablename, ','.join(names) , ','.join(values))))

def sql_update_set(kwargs):
    s_set = nice_dict(lambda k,w: "%s = %s" % (k,w),kwargs, ',')

def test_print(s,*args):
    print s % args
    return s % args

def _p(args):
    print args
    return args
