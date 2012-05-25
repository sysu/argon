from bases import Model,IdModel
from section import Section

class Board(IdModel):

    __idname__ = 'bid'
    __ = 'argo_boardhead'

    @classmethod
    def get_bid_by_name(cls,boardname):
        d = cls.db.get("SELECT bid FROM %s WHERE boardname = %%s" % cls.__ ,
                       boardname)
        return d and d['bid']

    @classmethod
    def get_board_by_sid(cls,sid):
        res = cls.db.query("SELECT * FROM %s WHERE sid = %%s" % cls.__,
                           sid)
        return cls.wrap_up(res)

    # def get_total(self):
    #     res = self.db.get("SELECT count(*) as total FROM %s%s" % (self.prefix,self["bid"]))
    #     return res

    # def get_topic_total(self):
    #     res = self.db.get("SELECT count(*) as total WHERE tid = 0 FROM %s%s" % (self.prefix,self["bid"]))
    #     return res
