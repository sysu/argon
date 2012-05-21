from base import Model,sql_str
import functools.wraps

def hook_after(after):
    def inner(f):
        @functools.wraps(f)
        def wrapper(*args,**kwargs):
            res = f(*args,**kwargs)
            after(*args,**kwargs)
            return res
        return wrapper
    return inner

class Section(Model):

    __tablename__ = 'argo_sectionhead'
    __cacheprefix__ = 'argo_sectionhead'
    
    @property
    def sql_id(self):
        return "sid = %s" % self['sid']

    def drop_cache(self):
        self.cache.drop_key(self['sid'])        

    @hook_after(drop_cache)
    def save(self):
        self['sid'] = self.table.insert(self.dump_attr())
        self.pull()

    @classmethod
    def _get_by_sectionname(cls,sectionname):
        res = cls.table.one('*',"sectionname = '%s'" % sectionname)
        return res and cls(**res)

    # @classmethod
    # def get_by_sectionname(cls,sectionname):
    #     if self.cacher.

    @classmethod
    def get_by_sid(cls,sid):
        res = cls.table.one('*',self.sql_id)
        return res and cls(**res)

    @classmethod
    def get_by_sid_cache(cls,sid):
        if self.cacher.exist(sid) :
            return self.cacher.get_dict(sid)
        res = cls.get_by_sid(sid)
        if res :
            self.cacher.save_dict(sid,res)
        return res

    @classmethod
    def all(cls):
        res = cls.table.filters()
        return cls.wrap_up(res)

    @classmethod
    def get_sid_by_name(cls,sectionname):
        d = cls.get_by_sectionname(sectionname)
        return d['id']
