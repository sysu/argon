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

class Board(Model):

    def __init__(self, boardname = 'Test'):
        """
            Init Board instance.
        """
        self.attr_list=['bid', 'sid', 'boardname', 'description', 'bm', 'flag', 'level', 'lastupdate'];

        super(Board,self).__init__()
        self.boardname = self.escape_string(boardname)
        self.table = 'argo_filehead_' + self.boardname
        self.connect()
        if self.init_board_info() < 0:
            print 'ERR: init board %s error' % boardname;

    def init_board_info(self):
        """
            Init Board info.
            According to database/argo_boardhead.sql
        """
        affect_rows = self.query("SELECT %s FROM argo_boardhead where boardname='%s'" % (','.join(self.attr_list), self.boardname))

        if affect_rows > 0:
            row = self.fetchone()
            for i in range(0, len(self.attr_list)):
                setattr(self, self.attr_list[i], row[i])
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
        self.query("SELECT %s FROM %s order by pid limit %d,%d " % (','.join(pattr_list), self.table, start, end-start))
        rows = self.fetchall()
        res = [Post(row) for row in rows]
        return res

    def get_total(self):
        """
            Get total post numbers
        """
        self.query("SELECT count(*) FROM %s" % self.table)
        row = self.fetchone()
        return row[0]

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
        exist_attr, exist_val = post.dump_attr()
        sql = "INSERT INTO %s(%s) values(%s)" % (self.table, ','.join(exist_attr), ','.join(exist_val))
        self.query(sql)

    def del_post(self, start, end = -1):
        """
            Del post from start to end, according to post time order increatment
        """
        if end == -1: end = self.get_total()
        if start > end: start = end;
        start_pid = start = self.get_post(start, start+1)[0].pid
        end_pid = self.get_post(end-1, end)[0].pid
        self.query("DELETE FROM %s WHERE pid >= %d and pid <= %d" % (self.table, start_pid, end_pid))

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
        exist_key, exist_val = post.dump_attr()
        key_eq_value = self.gen_update(zip(exist_key, exist_val), ['pid']);
        sql = "UPDATE %s SET %s where pid = %d" % (self.table, ','.join(key_eq_value), post.pid )
        self.query(sql)

    def close(self):
        self.closedb()


