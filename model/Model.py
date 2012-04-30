# -*- coding: utf-8 -*-

import dbapi
from globaldb import global_conn


class Model(object):

    def __init__(self):
        self.db = global_conn;

    def query(self, sql):
        res = self.db.query(sql)
        # print 'DEBUG: sql %s %d' % (sql,len(res))
        return res

    def escape_string(self, rawsql):
        safe_sql = self.db.escape_string(rawsql)
        return safe_sql

    def execute(self, sql):
        self.db.execute(sql)

    def toStr(sql, s):
        return "'"+str(s)+"'";

    def close():
        self.db.close()



"""
Board:
    `bid` int(11) unsigned NOT NULL auto_increment,
    `sid` int(11) unsigned NOT NULL, || section id
    `boardname` varchar(20) NOT NULL,
    `description` varchar(50) NOT NULL, || 版面描述
    `bm` varchar(80), || 版主
    `flag` int(11) unsigned default 0, || 版面属性, 见 const.h: BRD_* 常量
    `level` int(11) unsigned default 0, || read/post 权限 见 permissions.h: PERM_*
    `lastupdate` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP, || 最后发贴时间

"""
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

    def __getitem__(self, name):
        try:
            return self.dict[name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        self.dict[name] = value

    def init_board_info(self):
        """
            Init Board info.
            According to database/argo_boardhead.sql
        """
        res = self.query("SELECT * FROM argo_boardhead where boardname='%s'" % (self.boardname))

        if len(res) == 1:
            self.dict = res[0]
            return 0
        else:
            self.dict = {}
            return -1

    def get_post(self, start, end=-1):
        """
            Get post from start to end, according to { post time | pid }
            end = -1 means the last one
            Return  [Post1, Post2, ...]
        """
        if end == -1: end = self.get_total()
        if start > end: start = end

        rows = self.query("SELECT * FROM %s order by pid limit %d,%d " % (self.table, start, end-start))
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
        self.execute(sql)

    def del_post(self, start, end = -1):
        """
            Del post from start to end, according to post time order increatment
        """
        if end == -1: end = self.get_total()
        if start > end: start = end;
        start_pid = start = self.get_post(start, start+1)[0]['pid']
        end_pid = self.get_post(end-1, end)[0]['pid']
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
        return self.dict.items()


"""
Post:
    `pid` int(11) unsigned NOT NULL auto_increment,
    `bid` int(11) unsigned NOT NULL,
    `owner` varchar(14),  || author
    `realowner` varchar(14), || In anonymous board, owner is hidden. Use realowner to identify the author.
    `title` varchar(60),
    `flag` int(11)  unsigned default 0, || See consts.h:  FILE_*
    `tid` int(11) unsigned default 0, || tid = the first post's pid of this topic, to identify the same topic
    `replyid` int(11) unsigned, || The pid of the post this post replys
    `posttime` int(11) unsigned,
    `attachidx` varchar(20), || If has attach, this will be the index of the attach file.

    `fromaddr` varchar(64), || ip
    `fromhost` varchar(40) NOT NULL, || Host: Yat-sen Channel , Seems useless

    `content` text,
    `quote` text, || The quote of the reply post
    `signature` text, || Yes, signature.

    `agree` int(11) unsigned NOT NULL default 0, || How many users agree it.
    `disagree` int(11) unsigned NOT NULL default 0, || How many users disagree it.

"""
class Post(object):

    def __init__(self, dict = {}):
       self.dict = dict;

    def __getitem__(self, name):
        try:
            return self.dict[name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        self.dict[name] = value

    def dump_attr(self):
        return self.dict.items()



