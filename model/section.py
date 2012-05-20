from base import Model

class Section(Model):

    __tablename__ = 'argo_sectionhead'

    @classmethod
    def get_by_sectionname(cls,sectionname):
        return cls.table.one('*',"sectionname = %s" % sectionname)

    @classmethod
    def get_by_sid(cls,sid):
        return cls.table.one('*',"sid = %s" % sid)

    # @classmethod
    # def get_sid_by_name(cls,sectionname):
    #     d = cls.get_by_sectionname(sectionname)
    #     return d['id']
