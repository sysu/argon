from base import Model

class Section(Model):

    tablename = 'argo_sectionhead'

    @classmethod
    def get_by_sectionname(cls,sectionname):
        return cls.get(sectionname=sectionname)

    @classmethod
    def get_by_sid(cls,sid):
        return cls.get(sid=sid)

    @classmethod
    def get_sid_by_name(cls,sectionname):
        d = cls.get_by_sectionname(sectionname)
        return d['id']
