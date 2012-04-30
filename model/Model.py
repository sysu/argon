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

    def escape_attr(self, dict):
        res = {}
        for k,v in dict.items():
            if v != None:
                res[k] = v
        return res

    def toStr(self, s):
        return "'"+str(s)+"'";

    def close():
        self.db.close()

"""
    `sid` int(11) unsigned NOT NULL auto_increment,
    `sectionname` varchar(20) NOT NULL, || ie. 校园社团
    `description` varchar(50) NOT NULL, || ie. [休闲][娱乐]

    NOTE:
        由于section可以当作常量，系统init时load到全局中
"""

class Section(Model):

    def __init__(self, dict = {}):
        self.db = global_conn;
        self.dict = dict

    def __getitem__(self, name):
        try:
            return self.dict[name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        self.dict[name] = value

    def get_allboards(self):
        if not self.dict.has_key('sid'): return []

        sql = "SELECT boardname FROM argo_boardhead WHERE sid = %d" % self.dict['sid'];
        res = self.db.query(sql)
        return [Board(b['boardname']) for b in res]

"""
Board:
    `bid` int(11) unsigned NOT NULL auto_increment,
    `sid` int(11) unsigned NOT NULL, || 所属区id
    `boardname` varchar(20) NOT NULL,
    `description` varchar(50) NOT NULL, || 版面描述
    `bm` varchar(80), || 版主
    `flag` int(11) unsigned default 0, || 版面属性, 见 const.h: BRD_* 常量
    `level` int(11) unsigned default 0, || read/post 权限 见 permissions.h: PERM_*

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
            self.dict = self.escape_attr(res[0])
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

    def get_onepost(self, pos):
        """
            Get single Post
        """
        res = self.get_post(pos, pos+1)
        return res[0]

    def get_topic(self, start, end = -1):
        """
            Get topic(tid=0) from start to end-1 , [start, end)
            Order by pid
        """
        if start < 0: start = 0;
        if end <= start: end = start+1;
        sql = "SELECT * FROM %s WHERE tid = 0 ORDER BY pid LIMIT %d,%d" % (self.table, start, end-start)
        rows = self.query(sql)
        res = [Post(row) for row in rows]
        return res


    def get_total(self):
        """
            Get total post numbers
        """
        res = self.query("SELECT count(*) as total FROM %s" % self.table)
        row = res[0]
        return row['total']

    def get_topic_total(self):
        """
            Return how many Post.tid = 0
        """
        sql = "SELECT count(*) as total FROM %s WHERE tid = 0" % (self.table)
        res = self.query(sql)[0]
        return res['total']

    def get_last(self, limit = 20):
        """
            Get the last limit posts
            Return [Post1, Post2, ...]
        """
        end = self.get_total()
        start = end - limit
        if start <= 0: start = 0
        return self.get_post(start, end)

    def get_topic_last(self, limit = 20):
        """
            Get last limit topics' first posts
        """
        end = self.get_topic_total()
        start = end - limit;
        if start <= 0: start = 0
        return self.get_topic(start, end)

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
        start_pid = start = self.get_onepost(start)['pid']
        end_pid = self.get_onepost(end-1)['pid']
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
        if post['pid'] == None:
            return -1
        kv_pairs = post.dump_attr()
        k_e_v = [str(k)+"="+self.toStr(v) for k,v in kv_pairs]
        sql = "UPDATE %s SET %s where pid = %s" % (self.table, ','.join(k_e_v), post['pid'] )
        self.execute(sql)

    def update_board(self):
        """
            Update board
        """
        if self['bid'] == None:
            return -1
        kv_pairs = self.dump_attr()
        k_e_v = [str(k)+"="+self.toStr(v) for k,v in kv_pairs]
        sql = "UPDATE argo_boardhead SET %s where bid = %s" % (','.join(k_e_v), self['bid'] )
        self.execute(sql)

    def close(self):
        self.closedb()

    def dump_attr(self):
        return self.dict.items()


"""
Post:
    `pid` int(11) unsigned NOT NULL auto_increment,
    `bid` int(11) unsigned NOT NULL,
    `owner` varchar(14),  || 发贴人
    `realowner` varchar(14), || 在匿名版，owner会被hidden起来，用realowner标示真正作者
    `title` varchar(60),
    `flag` int(11)  unsigned default 0, || See consts.h:  FILE_*
    `tid` int(11) unsigned default 0, || 主题id，tid=本主题第一贴的pid，0表示为主题第一贴
    `replyid` int(11) unsigned, || 本贴回复的帖子id
    `posttime` int(11) unsigned, || 发贴时间, 用unix时间戳
    `attachidx` varchar(20), || 附件的index，附件不存数据库,直接存文件系统

    `fromaddr` varchar(64), || ip
    `fromhost` varchar(40) NOT NULL, || Host: Yat-sen Channel , 其实可以考虑去掉

    `content` text,
    `quote` text, || 回复帖子引用 [在 xxx 的大作中提到：
    `signature` text, || 签名档

    `agree` int(11) unsigned NOT NULL default 0, || 赞
    `disagree` int(11) unsigned NOT NULL default 0, || 踩 用于帖子分数统计
    `credit` int(11) NOT NULL deafult 0 || 分数,根据agree 和 disagree 计算,好贴自动浮起

"""
class Post(Model):

    def __init__(self, dict = {}):
       self.dict = self.escape_attr(dict)

    def __getitem__(self, name):
        try:
            return self.dict[name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        self.dict[name] = value

    def dump_attr(self):
        return self.dict.items()



