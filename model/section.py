from bases import IdModel

class Section(IdModel):

    __idname__ = 'sid'
    __ = 'argo_sectionhead'
    
    @classmethod
    def _get_by_sectionname(cls,sectionname):
        res = cls.table.one('*',"sectionname = '%s'" % sectionname)
        return res and cls(**res)

    # @classmethod
    # def get_sid_by_name(cls,sectionname):
    #     d = cls.get_by_sectionname(sectionname)
    #     return d['id']
