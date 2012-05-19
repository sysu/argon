from base import Model

class Board(Model):

    tablename = 'argo_boardhead'
    prefix = "argo_filehead_"
    
    def get_total(self):
        res = self.db.get("SELECT count(*) as total FROM %s%s" % (self.prefix,self["boardname"]))
        return res

    def get_topic_total(self):
        res = self.db.get("SELECT count(*) as total WHERE tid = 0 FROM %s%s" % (self.prefix,self["boardname"]))
        return res

    @classmethod
    def get_by_boardname(cls,boardname):
        return cls.get(boardname=boardname)

