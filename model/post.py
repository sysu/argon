# need to reconstruction after change the model base

from bases import IdModel
from MySQLdb import ProgrammingError
from board import Board

class Post(IdModel):

    table_prefix = "argo_filehead_"
    __idname__ = "pid"

    @classmethod
    def tablename(cls,bid):
        return cls.table_prefix + bid
    
    @property
    def __(self):
        if self['bid'] is None:
            raise ValueError('No such board.')
        return self.table_prefix + str(self['bid'])

    def save(self):
        try:
            super(Post,self).save()
        except ProgrammingError,e:
            print 'Table[%s]' % self.__
            if e[0] == 1146 : # no exist table
                self._create_table(self['bid'])
                super(Post,self).save()
            else:
                import traceback
                traceback.print_exc()
                print
                raise e

    @classmethod
    def _create_table(cls,bid):
        import config
        from string import Template
        with open(config.SQL_TPL_DIR + 'template/argo_filehead.sql') as f :
            board_template = Template(f.read())
            cls.db.execute(board_template.safe_substitute(bid=bid))

    @classmethod
    def get_by_bid(cls, bid, offset, limit=20):
        res = cls.db.query("SELECT * FROM %s ORDER BY bid LIMIT %d,%d" % \
                               (cls.tablename(str(bid)) , offset, limit))
        return cls.wrap_up(res)

    # @classmethod
    # def all_topic(cls,boardname,start,limit):
    #     res = cls.db.query("SELECT * FROM %s WHERE tid = 0 ORDER BY id LIMIT %d,%d",self.tablename,start,limit)
    #     return cls.wrap_up(res)

    @classmethod
    def add(cls,userid,boardname,content,**kwargs):
        kwargs['owner'] = userid
        kwargs['bid'] = Board.get_bid_by_name(boardname)
        p = Post(**kwargs)
        p.save()

    # @classmethod
    # def init(cls):
    #     print '*' * 70
    #     print "You need to clear and add the argo_filehead_* manually"
    #     print '*' * 70
    #     raw_input()
