__metaclass__ = type

from globaldb import global_conn
from globaldb import global_cache

class Table:

    def __init__(self,tablename=None,db=global_conn):
        self.db = global_db
        if tablename is not None:
            self.bind(tablename)

    def __set__(self,obj,val):
        raise Exception(u'Should never set value to db')

    def bind(self,tablename):
        self.tablename = tablename
        self._sql_filters   = "SELECT * FROM %s WHERE %%s"        % tablename
        self._sql_filters_n = "SELECT * FROM %s"                  % tablename
        self._sql_delete    = "DELETE FROM %s WHERE %%s "         % tablename
        self._sql_insert    = "INSERT INTO %s (%%s) VALUES (%%s)" % tablename
        self._sql_update    = "UPDATE %s SET %%s WHERE %%s"       % tablename
        self._sql_select    = "SELECT %%s FROM %s WHERE %%s"

    def select(self,what,condition):
        return self.db.query(self._sql_select,what,condition)

    def one(self,what,condition):
        return self.db.one(self._sql_select,what,condition)
        
    def filters(self,condition=None):
        if condition is not None :
            res = self.db.query(self._sql_filters,condition)
        else :
            res = self.db.query(self._sql_filters_n)
        return res

    def delete(self,condition):
        self.db.execute(self._sql_delete,condition)
        
    def insert(self,kwargs):
        names,values = zip(*kwargs.items())
        return self.db.execute(self._sql_insert, ','.join(names), ','.join(values))

    def update(self,kwargs,condition):
        action = nice_dict("%s = %s",kwargs,',')
        return self.db.execute(self._sql_update,action,condition)

class MetaModel(type):
    
    def __new__(cls,names,bases,attrs):
        super(MetaModel,cls).__new__(cls,names,bases,attrs)
        if '__database__' in attrs :
            cls.db = __database__
        if attrs.get('__tablename__') is not None :
            if hasattr(cls,'db') :
                cls.table = Table(attrs['__tablename__'],cls.db)
            else :
                cls.table = Table(attrs['__tablename__'])
        return cls

class Model:

    __metaclass__ = MetaModel
    __tabelename__ = None

    db = global_conn
    cache = global_cache
    
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
                             nice_dict(lambda k,w : "%s:%s",
                                       self.items()))

    @property
    def sql_id(self):
        return "id = %s" % self['id']

    def save(self):
        self.table.insert(self.dump_attr())
        self.pull()

    def update(self):
        self['id'] = self.table.update(self.dump_attr(),self.sql_id)

    def pull(self):
        self.dict = self.table.one('*',self.sql_id)

    def delete(self):
        self.delete(self.sql_id)

    ##############################
    # base for orm               #
    ##############################

    @classmethod
    def escape_string(cls,rowsql):
        pass
    
    @classmethod
    def wrap_up(cls,res):
        return [ cls(**res) for x in res]

def nice_dict(lbd_format,dic,seq=' '):
    buf = reduce(lambda p,x : p.append(lbd_format(x[0],x[1])),
                 dic.items,[])
    return seq.join(buf)
