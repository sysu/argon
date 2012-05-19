from base import Model

class Section(Model):

    tablename = 'argo_sectionhead'

    @classmethod
    def get_by_sectionname(cls,sectionname):
        return cls.get(sectionname=sectionname)

    @classmethod
    def get_by_sid(self,sid):
        return cls.get(sid=sid)

    

