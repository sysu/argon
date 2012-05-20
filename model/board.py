from base import Model

class Board(Model):

    tablename = 'argo_boardhead'
    prefix = "argo_filehead_"

    def get_total(self):
        res = self.db.get("SELECT count(*) as total FROM %s%s" % (self.prefix,self["bid"]))
        return res

    def get_topic_total(self):
        res = self.db.get("SELECT count(*) as total WHERE tid = 0 FROM %s%s" % (self.prefix,self["bid"]))
        return res

    @classmethod
    def get_by_boardname(cls,boardname):
        return cls.get(self.tablename,'*',"boardname = %s",boardname)

    @classmethod
    def get_by_bid

    @classmethod
    def get_id_by_name(cls,boardname):
        b = cls.get_by_boardname(boardname)
        return b['id']
