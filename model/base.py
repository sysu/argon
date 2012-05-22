__metaclass__ = type

from globaldb import global_conn
from globaldb import global_cache

from functools import wraps

class Table:

    def __init__(self,tablename=None,db=None):
        self.bind(tablename,db)
        
    def __set__(self,obj,val):
        raise Exception(u'Should never set value to Table')

    def bind(self,tablename=None,db=None):
        if tablename is not None :
            self.tablename = tablename
            self._sql_filters   = "SELECT * FROM %s WHERE %%s"        % tablename
            self._sql_filters_n = "SELECT * FROM %s"                  % tablename
            self._sql_delete    = "DELETE FROM %s WHERE %%s "         % tablename
            self._sql_insert    = "INSERT INTO %s (%%s) VALUES (%%s)" % tablename
            self._sql_update    = "UPDATE %s SET %%s WHERE %%s"       % tablename
            self._sql_select    = "SELECT %%s FROM %s WHERE %%s"      % tablename
        if db is not None:
            self.db = db

    def select(self,what,condition):
        return self.db.query(self._sql_select,what,condition)

    def one(self,what,condition):
        return self.db.get(self._sql_select % (what,condition))
        
    def filters(self,condition=None):
        if condition is not None :
            res = self.db.query(self._sql_filters,condition)
        else :
            res = self.db.query(self._sql_filters_n)
        return res

    def delete(self,condition):
        self.db.execute(self._sql_delete % condition)
        
    def insert(self,kwargs):
        names,values = zip(*kwargs.items())
        return self.db.execute(self._sql_insert % ( ','.join(names),
                                                    ','.join(map(sql_str,values))))

    def update(self,kwargs,condition):
        action = nice_dict("%s = %s",kwargs,',')
        return self.db.execute(self._sql_update,action,condition)

class MetaModel(type):
    
    def __new__(cls,names,bases,attrs):
        cls = super(MetaModel,cls).__new__(cls,names,bases,attrs)
        if '__database__' in attrs :
            cls.db = __database__
        for key,val in attrs.items() :
            if isinstance(val,Table) and val.db is None :
                val.bind(cls.db)
        # For cacher
        if attrs.get('__cacheprefix__') is not None:
            if attrs.get('__cache__') is None:
                cls.cacher = Cacher(attrs['__cacheprefix__'])
            else:
                cls.cacher = Cacher(attrs['__cacherprefix__'],cls.__cache__)
        return cls

class Model:

    __metaclass__ = MetaModel
    __database__ = global_conn

    #######################
    # for record in model #
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
                             nice_dict(lambda k,w : "'%s':'%s'" % (k,w),
                                       self.dump_attr(),','))

    ##############################
    # base for orm               #
    ##############################

    @classmethod
    def escape_string(cls,rowsql):
        pass
    
    @classmethod
    def wrap_up(cls,res):
        return [ cls(**x) for x in res]
    

class SingleModel(Model):

    '''
    Model with one table.
    ! Need to set the ``table`` attr of class.
    '''
    
    @property
    def sql_id(self):
        return "id = %s" % self['id']

    def save(self):
        self['id'] = self.table.insert(self.dump_attr())
        self.pull()

    def update(self):
        self['id'] = self.table.update(self.dump_attr(),self.sql_id)

    def pull(self):
        self.dict = self.table.one('*',self.sql_id)

    def delete(self):
        self.table.delete(self.sql_id)

def nice_dict(lbd_format,dic,seq=' '):
    buf = map(lambda x : lbd_format(*x),dic.items())
    return seq.join(buf)

def sql_str(data):
    return "'%s'" % data
