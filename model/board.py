from bases import Model,IdModel

class Board(IdModel):

    __idname__ = 'bid'
    __ = 'argo_boardhead'
    
    # def get_total(self):
    #     res = self.db.get("SELECT count(*) as total FROM %s%s" % (self.prefix,self["bid"]))
    #     return res

    # def get_topic_total(self):
    #     res = self.db.get("SELECT count(*) as total WHERE tid = 0 FROM %s%s" % (self.prefix,self["bid"]))
    #     return res
