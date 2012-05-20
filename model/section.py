from base import Model,sql_str

class Section(Model):

    __tablename__ = 'argo_sectionhead'

    @property
    def sql_id(self):
        return "sid = %s" % self['sid']

    def save(self):
        self['sid'] = self.table.insert(self.dump_attr())
        self.pull()

    @classmethod
    def get_by_sectionname(cls,sectionname):
        res = cls.table.one('*',"sectionname = '%s'" % sectionname)
        return res and cls(**res)

    @classmethod
    def get_by_sid(cls,sid):
        res = cls.table.one('*',self.sql_id)
        return res and cls(**res)

    @classmethod
    def all(cls):
        res = cls.table.filters()
        return cls.wrap_up(res)

    # @classmethod
    # def get_sid_by_name(cls,sectionname):
    #     d = cls.get_by_sectionname(sectionname)
    #     return d['id']
