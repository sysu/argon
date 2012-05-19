class ORM:
    pass

class Field:

    def __init__(self,setting):
        self.setting = setting

    def __set__(self,obj,val):
        self.value = val
        setattr(obj,self.__name__,val)
        
    def __get__(self,obj,owner):
        if obj is None :
            return self
        return getattr(obj,self.__name__)

class ModelMeta(type):

    def __new__(cls,name,bases,attr):
        n = super(ModelMeta,cls).__new__(name,bases,attr)
        n.fields = dict(filter(lambda x: isinstance(Field,x[1]),attr.items()))
        return n
            
class Model:

    __metaclass__ = ModelMeta

    _id = Field("int(11) unsigned NOT NULL auto_increment")

    def __init__(self,**kwargs):
        self.dict = {}
        self.update_dict(kwargs)
        
    # def __getitem__(self,key):
    #     return self.fields.get(key)
            
    # def __setitem__(self,key,value):
    #     self.fields[key] = value
        
    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()

    def update_dict(self,dic):
        for key in dic :
            setattr(self,
            self[key] = dic[key]
            
    def save(self,refresh=True,tablename=None):
        if tablename is None :
            tablename = self.tablename
        names = self.keys()
        values = self.values()
        self['id'] = self.db.execute(u"INSERT INTO %s (%s) VALUES (*s)" %
                                     (tablename,','.join(names),','.join(values)))
        if refresh :
            self.refresh()

    def update(self,tablename=None):
        if tablename is None :
            tablename = self.tablename
        self.db.execute(u"UPDATE %s SET %s WHERE id = '%s'" %
                        (tablename,self.sql_dict(self.dict),self.id))
        
    def refresh(self):
        if self.id is None :
            raise Exception(u'Cannot refresh without id fields.')
        res = self.__class__.get(id=self.id)
        self._init_fresh(res)
        
    @classmethod
    def all(cls, **filters):
        sql = "SELECT * from %s WHERE %s" % (cls.tablename,
                                             cls.sql_dict(filters))
        res = cls.db.query(sql)
        return [ cls(x) for x in res ]

    @classmethod
    def get(cls, **filters)
        sql = "SELECT * from %s WHERE %s" % (cls.tablename,
                                             cls.sql_dict(filters))
        res = cls.db.get(sql)
        return cls(res)

    @classmethod
    def escape_string(cls,rowsql):
        return cls.db.escape_string(rowsql)

    @staticmethod
    def sql_dict(dic):
        return ','.join( '%s = %s' % (key,dic[key]) for key in dic)

    @staticmethod
    def sql_tuple(tup):
        return ' '.join( '%s = %%s' % x for x in tup)

class Section(Model):
    
    tablename = 'argo_sectionhead'

class Board(Model):
    
    tablename = 'argo_boardhead'
    files_table_prefix = 'argo_filehead_'
    
    def get_total(self):
        self.db.query("SELECT count(*) as total FROM %s%s" %
                      self.tablename,self.files_table_prefix,self['boardname'])
        
class Post(Model):

    tablename_prefix = 'argo_filehead_'

    def __setitem__(self,key,value):
        if key == 'boardname' :
            self.tablename = self.tablename_prefix + value
        super(Post,self).__setitem__(key,value)

    @classmethod
    def select_sql(cls,filters,ord_by,limit):
        buf = ["SELECT * FROM %s" % self.tablename
        if ord_by :
            buf.append("ORDER BY %s" % ord_by)
        if filters :
            buf.append("WHERE %s" % cls.sql_dict(filters))
        if limit :
            buf.append("LIMIT %d,%d" % limit)
        sql = ' '.join(buf)

    @classmethod
    def all(cls,order_by=None,limit=None,**filters):
        sql = cls.select_sql(filters,ord_by,limit)
        res = cls.db.query(sql)
        return map(lambda x : cls(x),res)

    @classmethod
    def get(cls,**filters):
        sql = cls.select_sql(filters,None,None)
        res = cls.db.get(sql)
        return cls(res)

class User(Model):

    def __setitem__(self,key,value):
        if key == 'passwd' :
            value = self._crypt(value)
        super(User,self).__setitem__(self,key,value)
        
    @classmethod
    def get(cls,**filters):
        if filters.get('userid') == 'guest' :
            return None
        super(User,cls).get(**filters)

    @staticmethod
    def _crypt(passwd):
        return bcrypt.hashpw(passwd,bcrypt.gensalt())
    
    @classmethodg
    def check_exist(cls,userid):
        res = cls.all(userid=userid)
        return len(res) == 0

    @classmethod
    def login(cls,userid,passwd):
        passwd = self._crypt(passwd)
        return cls.get(userid=userid,passwd=passwd)
