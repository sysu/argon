from base import SingleModel,Table

class Board(SingleModel):

    tablen = Table('argo_boardhead')

    prefix = 'argo_filehead_'

    # def get_total(self):
    #     res = self.db.get("SELECT count(*) as total FROM %s%s" % (self.prefix,self["bid"]))
    #     return res

    # def get_topic_total(self):
    #     res = self.db.get("SELECT count(*) as total WHERE tid = 0 FROM %s%s" % (self.prefix,self["bid"]))
    #     return res

    @classmethod
    def get_by_boardname(cls,boardname):
        return cls.table.one('*',"boardname = '%s'" % boardname)

    @classmethod
    def get_by_bid(cls,bid):
        return cls.table.one('*',"bid = %d" % bid)
