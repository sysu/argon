from bases import IdModel

class Section(IdModel):

    __idname__ = 'sid'
    __ = 'argo_sectionhead'
    
    # @classmethod
    # def get_by_sectionname(cls,sectionname):
    #     res = cls.table.one('*',"sectionname = '%s'" % sectionname)
    #     return res and cls(**res)

    @classmethod
    def get_by_sectionname(cls,sectionname):
        res = cls.db.get("SELECT * FROM %s WHERE sectionname = %%s" % cls.__, sectionname)
        return res and cls(**res)

    # @classmethod
    # def get_sid_by_name(cls,sectionname):
    #     d = cls.get_by_sectionname(sectionname)
    #     return d['id']
