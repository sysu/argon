from base import Model

class Post(Model):

    table_prefix = "argo_filehead_"

    def __setitem__(self,key,value):
        if key == 'boardname' :
            self.tablename = self.table_prefix + value
        super(Post,self).__setitem__(key,value)

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

