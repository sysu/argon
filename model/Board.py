from Model import Model
from Post import Post
"""
    `bid` int(11) unsigned NOT NULL auto_increment,
    `sid` int(11) unsigned NOT NULL,
    `boardname` varchar(20) NOT NULL,
    `description` varchar(50) NOT NULL,
    `bm` varchar(80),
    `flag` int(11) unsigned default 0,
    `level` int(11) unsigned default 0,
    `lastupdate` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,

"""

board_attr_list = ['bid','sid','boardname','description','flag','level','lastupdate']

class Board(Model):

    def __init__(self, boardname = 'Test'):
        """
            Init Board instance.
        """
        super(Board, self).__init__()
        self.boardname = self.escape_string(boardname)
        self.table = 'argo_filehead_' + self.boardname

        if self.init_board_info() < 0:
            print 'ERR: init board %s error' % boardname;

    def init_board_info(self):
        """
            Init Board info.
            According to database/argo_boardhead.sql
        """
        self.attr_list = board_attr_list
        res = self.query("SELECT %s FROM argo_boardhead where boardname='%s'" % (','.join(self.attr_list), self.boardname))

        if len(res) == 1:
            row = res[0]
            for att in self.attr_list:
                setattr(self, att, row[att])
            return 0
        else: return -1

    def get_post(self, start, end=-1):
        """
            Get post from start to end, according to { post time | pid }
            end = -1 means the last one
            Return  [Post1, Post2, ...]
        """
        if end == -1: end = self.get_total()
        if start > end: start = end

        pattr_list = Post().attr_list;
        rows = self.query("SELECT %s FROM %s order by pid limit %d,%d " % (','.join(pattr_list), self.table, start, end-start))
        res = [Post(row) for row in rows]
        return res

    def get_total(self):
        """
            Get total post numbers
        """
        res = self.query("SELECT count(*) as total FROM %s" % self.table)
        row = res[0]
        return row['total']

    def get_last(self, limit = 20):
        """
            Get the last limit posts
            Return [Post1, Post2, ...]
        """
        end = self.get_total()
        start = end - limit
        if start <= 0: start = 0
        return self.get_post(start, end)


    def add_post(self, post):
        """
            Add post.
            TODO: escape string
        """
        kv_pairs = post.dump_attr()
        exist_attr = [k for k,v in kv_pairs]
        exist_val = [self.toStr(v) for k,v in kv_pairs]
        sql = "INSERT INTO %s(%s) values(%s)" % (self.table, ','.join(exist_attr), ','.join(exist_val))
        print sql
        self.execute(sql)

    def del_post(self, start, end = -1):
        """
            Del post from start to end, according to post time order increatment
        """
        if end == -1: end = self.get_total()
        if start > end: start = end;
        start_pid = start = self.get_post(start, start+1)[0].pid
        end_pid = self.get_post(end-1, end)[0].pid
        self.execute("DELETE FROM %s WHERE pid >= %d and pid <= %d" % (self.table, start_pid, end_pid))

    def del_last(self, limit = 20):
        """
            Del the last limit posts
        """
        end = self.get_total()
        start = end - limit
        if start <= 0: start = 0
        self.del_post(start, end)

    def update_post(self, post):
        """
            Update post information.
        """
        if not hasattr(post, 'pid'):
            return -1
        kv_pairs = post.dump_attr()
        k_e_v = [str(k)+"="+self.toStr(v) for k,v in kv_pairs]
        sql = "UPDATE %s SET %s where pid = %d" % (self.table, ','.join(k_e_v), post.pid )
        self.execute(sql)

    def close(self):
        self.closedb()

    def dump_attr(self):
        return [(k, getattr(self,k)) for k in self.attr_list if hasattr(self,k)]

