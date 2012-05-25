from bases import IdModel,Cacher

class Section(IdModel):

    __idname__ = 'sid'
    __ = 'argo_sectionhead'

    id2name_cache = Cacher('section_sid')
    
    # @classmethod
    # def get_by_sectionname(cls,sectionname):
    #     res = cls.table.one('*',"sectionname = '%s'" % sectionname)
    #     return res and cls(**res)

    @classmethod
    def _get_sid_by_name(cls,sectionname):
        d = cls.db.get("SELECT sid FROM %s WHERE sectionname = %%s" % cls.__,
                       sectionname)
        return d and d['sid']

    @classmethod
    def get_sid_by_name(cls,sectionname):
        d = cls.id2name_cache.hget(sectionname)
        if d :
            return d
        else :
            d = cls._get_sid_by_name(sectionname)
            if d :
                cls.id2name_cache.hmset(field, d)
                return d
