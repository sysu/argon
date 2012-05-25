#!/usr/bin/python2
# -*- coding: utf-8 -*-

__metaclass__ = type

from globaldb import global_conn
from globaldb import global_cache

class MetaModel(type):

    def __new__(cls,names,bases,attrs):
        cls = super(MetaModel,cls).__new__(cls,names,bases,attrs)
        if attrs.get('__clsinit__') :
            cls.__clsinit__(names,bases,attrs)
        if cls.ch is not None:
            for key in attrs:
                attr = attrs[key]
                if isinstance(attr,Cacher) and attr.ch is None:
                    attr.bind(ch=cls.ch)
        return cls

class Cacher:

    _prefix = 'argo_'

    def __init__(self,prefix,ch=None):
        self.ch = None
        self.bind(prefix,ch)

    def bind(self,prefix=None,ch=None):
        if prefix :
            self.__ = self._prefix + prefix
        if ch :
            self.ch = ch

    def exists(self):
        return self.ch.exists(self.__)

    def hgetall(self):
        return self.ch.hgetall(self.__)

    def hget(self,field):
        return self.ch.hget(self.__, field)

    def hmset(self,field):
        return self.ch.hmset(self.__,field)

    def scard(self):
        return self.ch.scard(self.__)

    def sadd(self,mem):
        return self.ch.sadd(self.__, mem)

    def srem(self,mem):
        return self.ch.srem(self.__, mem)

class Model:

    __metaclass__ = MetaModel
    
    db = global_conn
    ch = global_cache
    
    #######################
    # for record in table #
    #######################
    
    def __init__(self,**attr):
        self.dict = {}
        self.update_dict(attr)
        
    def __getitem__(self,key):
        return self.dict.get(key)
            
    def __setitem__(self,key,value):
        self.dict[key] = value

    def update_dict(self,dic):
        self.dict.update(dic)

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
    def tb_get_all_nw(cls,tablename):
        return cls.db.query("SELECT * FROM %s" % cls.__)

    @classmethod
    def tb_get_all(cls,tablename=None):
        return cls.wrap_up(cls.tb_get_all_nw(tablename))

    @classmethod
    def tb_insert_dict(cls,tablename,dic):
        ''' Change to INSERT INTO tablename (col1,col2,col3..) VALUES (%s,%s,%s...),
        and auto escape string. '''
        names,values = zip(*dic.items())
        sql = "INSERT INTO %s (%s) VALUES (%s)" % \
            (tablename, ','.join(names) , ','.join(['%s'] * len(values)))
        return cls.db.execute(sql,*values)
    
    @classmethod
    def get_all_nw(cls):
        return cls.tb_get_all_nw(cls.__)

    @classmethod
    def get_all(cls):
        return cls.tb_get_all(cls.__)

    # @classmethod
    
    
class IdModel(TableModel):

    __idname__ = 'id'
    __ = None
    
    @property
    def id(self):
        return self.dict[self.__idname__]

    def save(self):
        self[self.__idname__] = self.tb_insert_dict(self.__,self.dump_attr())
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
        res = self.tb_get_nw(self.__, self.__idname__, self.id)
        self.dict = res

    @classmethod
    def tb_get_nw(cls, tablename, idname, _id):
        return cls.db.get("SELECT * FROM %s WHERE %s = %%s" %\
                                ( tablename, idname),
                            _id)

    @classmethod
    def tb_get(cls, tablename, _id):
        res = cls.tb_get_nw(tablename, cls.__idname__, _id)
        return res and cls(**res)

    @classmethod
    def get(cls, _id):
        return cls.tb_get(cls.__,_id)

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

