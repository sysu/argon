__metaclass__ = type

from globaldb import global_conn
from globaldb import global_cache

class Model:

    db = global_conn
    cache = global_cache

    #######################
    # for record in table #
    #######################
    
    def __init__(self,**kwargs):
        self.dict = kwargs
        
    def __getitem__(self,key):
        return self.dict.get(key)
            
    def __setitem__(self,key,value):
        self.dict[key] = value

    def items(self):
        return self.dict

    def items_safe(self):
        return self.dict.copy()
    
    def __str__(self):
        return "<%s>{%s}" % (self.__class__.__name__,
                             self.nice_dict(lambda k,w : "%s:%s",
                                            self.items()))
        
    def remove(self):
        self.delete(self.tablename,"id = %s" % self['id'])
        self.dict = {}

    def save(self,refresh=False):
        self['id'] = self.insert(self.tablename,self.dict)
        if refresh :
            self.refresh()
            
    def push(self):
        self.update(self.tablename,self.nice_dict(lambda k,w: '%s = %s' % (k,w),
                                                  self.dict,','),
                    'id = %s' % self['id'])
                
    def refresh(self):
        self.dict = self.select('*',self.tablename,'id = %s' % self['id'])

    ####################
    # method for table #
    ####################

    @classmethod
    def filters(cls,condition=None):
        if condition is not None :
            res = cls.db.query("SELECT * FROM %s WHERE %s" % (cls.tablename,
                                                              condition))
        else :
            res = cls.db.query("SELECT * FROM %s" % cls.tablename)
        return [ cls(**x) for x in res]
    
    @classmethod
    def delete(cls,tablename,condition):
        self.db.execute("DELETE FROM %s WHERE %s" %\
                            (tablename,condition))

    ##############################
    # sick wraper                #
    ##############################
        
    @classmethod
    def insert(cls,tablename,kwargs):
        names,values = zip(*kwargs.items())
        sql = "INSERT INTO %s (%s) VALUES (%s)" %\
            (tablename,','.join(names),','.join(values))
        return cls.db.execute(sql)

    @classmethod
    def update(cls,tablename,action,condition):
        cls.db.execute("UPDATE %s SET %s WHERE %s",
                       (tablename,action,condition))

    @classmethod
    def select(cls,tablename,what,condition):
        return cls.db.query("SELECT %s FROM %s WHERE %s" %\
                                (what,tablename,condition))

    @classmethod
    def get(cls,tablename,what,condition):
        return cls.db.get("SELECT %s FROM %s WHERE %s" %\
                              (what,tablename,condition))

    @classmethod
    def drop(cls,tablename):
        cls.db.execute("DROP TABLE IF EXISTS `%s`",tablename)
        
    @classmethod
    def init(cls,tablename):
        import config
        with open("%s%s.sql" % (config.SQL_TPL_DIR, tablename)) as f:
            sql = f.read()
            cls.db.execute(sql)

    @classmethod
    def bind(cls,tablename):
        cls.tablename = tablename

    ##############################
    # base for orm               #
    ##############################

    @classmethod
    def escape_string(cls,rowsql):
        return cls.db.escape_string(rowsql)

    @classmethod
    def wrap_up(cls,res):
        return [ cls(**res) for x in res]
    
    @staticmethod
    def nice_dict(lbd_format,dic,seq=' '):
        buf = reduce(lambda p,x : p.append(lbd_format(x[0],x[1])),
                     dic.items,[])
        return seq.join(buf)
