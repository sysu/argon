# need to reconstruction after change the model base

from base import Model
from MySQLdb import ProgrammingError

class Post(Model):

    table_prefix = "argo_filehead_"

    def save(self,refresh=True):
        print 'Table[%s]' % self.tablename
        try:
            super(Post,self).save(refresh)
        except ProgrammingError,e:
            if e[0] == 1146 : # no exist table
                self.create_table(self['bid'])
                super(Post,self).save(refresh)
            else:
                import traceback
                traceback.print_exc()
                print
                raise e

    def refresh(self):
        if self['id'] is None or self['bid'] is None :
            raise Exception(u'Cannot refresh without id or bid fields.')
        res = self.get(id=self['id'],bid=self['bid'])
        self.dict = res

    @classmethod
    def create_table(cls,bid):
        import config
        from string import Template
        with open(config.SQL_TPL_DIR + 'template/argo_filehead.sql') as f :
            board_template = Template(f.read())
            cls.db.execute(board_template.safe_substitute(bid=bid))

    @classmethod
    def all(cls,**filters):
        try:
            tablename = cls.table_prefix + str(filters['bid'])
        except keyError :
            raise Exception(u'Need bid to seach the post.')
        res = cls.select(tablename,filters)
        return [ cls(**x) for x in res]

    @classmethod
    def get(cls,**filters):
        try:
            tablename = cls.table_prefix + str(filters['bid'])
        except KeyError:
            raise Exception(u'Need bid to seach the post.')
        sql = "SELECT * from %s WHERE %s" % (tablename,
                                             cls.sql_dict(filters,' AND '))
        print sql
        res = cls.db.get(sql)
        return res and cls(**res)
                
    @property
    def tablename(self):
        return "%s%s" % (self.table_prefix,str(self['bid']))

    @classmethod
    def all_by_boardname(cls,boardname,start,limit):
        res = cls.db.query("SELECT * FROM %s ORDER BY id LIMIT %d,%d",self.tablename,start,limit)
        return cls.wrap_up(res)

    @classmethod
    def all_topic(cls,boardname,start,limit):
        res = cls.db.query("SELECT * FROM %s WHERE tid = 0 ORDER BY id LIMIT %d,%d",self.tablename,start,limit)
        return cls.wrap_up(res)

    @classmethod
    def add(cls,userid,boardname,**kwargs):
        kwargs['userid'] = userid
        kwargs['boardname'] = boardname
        p = Post(**kwargs)
        p.save()

    @classmethod
    def init(cls):
        print '*' * 70
        print "You need to clear and add the argo_filehead_* manually"
        print '*' * 70
        raw_input()
