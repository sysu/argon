from globaldb import global_conn
from globaldb import global_cache

class Model:

    db = global_conn
    cache = global_cache

    #######################
    # for record in table #
    #######################
    
    def __init__(self,**kwargs):
        self.dict = {}
        self.update_dict(kwargs)
        
    def __getitem__(self,key):
        return self.dict.get(key)
            
    def __setitem__(self,key,value):
        self.dict[key] = value
        
    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()

    def update_dict(self,dic):
        # call the __setitem__ not simplily dict.update
        for key in dic :
            self[key] = dic[key]

    def delete(self):
        self.db.execute("DELETE FROM %s WHERE id = '%s'",
                        self.tablename,self['id'])
        self.dict = {}
            
    def save(self,refresh=True):
        names = self.keys()
        values = map(lambda x: self.sql_value(x),self.values())
        sql = u"INSERT INTO %s (%s) VALUES (%s)" %\
                                     (self.tablename, ','.join(names), ','.join(values))
        self['id'] = self.db.execute(sql)
        if refresh :
            self.refresh()

    def update(self):
        self.db.execute(u"UPDATE %s SET %s WHERE id = '%s'" %
                        (self.tablename,self.sql_dict(self.dict),self.id))
        
    def refresh(self):
        if self['id'] is None :
            raise Exception(u'Cannot refresh without id fields.')
        res = self.__class__.get(id=self['id'])
        self._init_fresh(res)

    ####################
    # method for table #
    ####################

    @classmethod
    def drop(cls):
        cls.db.execute("DROP TABLE IF EXISTS `%s`",cls.tablename)

    @classmethod
    def create(self):
        raise NotImplementedError

    @classmethod
    def init(self):
        self.drop()
        self.create()
        
    @classmethod
    def bind(cls,tablename):
        cls.tablename = tablename

    @classmethod
    def wrap_up(cls,res):
        return [ cls(**res) for x in res]
        
    @classmethod
    def all(cls, **filters):
        if filters :
            sql = "SELECT * FROM %s WHERE %s" % (cls.tablename,
                                                 cls.sql_dict(filters))
        else :
            sql = "SELECT * FROM %s" % cls.tablename
        res = cls.db.query(sql)
        return [ cls(**x) for x in res ]

    @classmethod
    def get(cls, **filters):
        sql = "SELECT * from %s WHERE %s" % (cls.tablename,
                                             cls.sql_dict(filters))
        res = cls.db.get(sql)
        return cls(res)

    @classmethod
    def escape_string(cls,rowsql):
        return cls.db.escape_string(rowsql)

    @classmethod
    def sql_dict(cls,dic):
        return ','.join( "%s = %s" % (key,cls.sql_value(dic[key])) for key in dic)

    @classmethod
    def sql_tuple(cls,tup):
        return ' '.join( '%s = %%s' % x for x in tup)

    @classmethod
    def sql_value(cls,value):
        return "'"+str(value)+"'"
