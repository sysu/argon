# -*- coding: utf-8 -*-

import dbapi
from globaldb import global_conn
import config

class Model(object):

    def __init__(self):
        self.db = global_conn;

    def __getitem__(self, name):
        try:
            return self.dict[name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        self.dict[name] = value

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

    def insert_dict(self,table,kv_pairs):
        exist_attr = kv_pairs.keys()
        exist_val = map(lambda x : self.to_str(x),kv_pairs.values())
        sql = "INSERT INTO %s(%s) values(%s)" % (table, ','.join(exist_attr), ','.join(exist_val))
        self.execute(sql)

    def to_str(self, s):
        return "'"+unicode(s)+"'";

    def close():
        self.db.close()

    def dump_attr(self):
        pass

"""
    `sid` int(11) unsigned NOT NULL auto_increment,
    `sectionname` varchar(20) NOT NULL, || ie. 校园社团
    `description` varchar(50) NOT NULL, || ie. [休闲][娱乐]

    NOTE:
        由于section可以当作常量，系统init时load到全局中
"""

class Section(Model):

    def __init__(self, sectionname,dict = {}):
        self.db = global_conn;
        self.sectionname = sectionname
        self.dict = dict
        self.init_section_info()

    def __getitem__(self, name):
        try:
            return self.dict[name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        self.dict[name] = value

    def init_section_info(self):
        res = self.query("SELECT * FROM argo_sectionhead where sectionname='%s'" % self.sectionname)

        if len(res) == 1:
            self.dict = self.escape_attr(res[0])
            return 0
        else:
            self.dict = {}
            return -1

    def get_allboards(self):
        if not self.dict.has_key('sid'): return []

        sql = "SELECT boardname FROM argo_boardhead WHERE sid = %d" % self.dict['sid'];
        res = self.db.query(sql)
        return [Board(b['boardname']) for b in res]

    def dump_attr(self):
        return self.dict.items()

"""
Board:
    `bid` int(11) unsigned NOT NULL auto_increment,
    `sid` int(11) unsigned NOT NULL, || 所属区id
    `boardname` varchar(20) NOT NULL,
    `description` varchar(50) NOT NULL, || 版面描述
    `bm` varchar(80), || 版主
    `flag` int(11) unsigned default 0, || 版面属性, 见 const.h: BRD_* 常量
    `level` int(11) unsigned default 0, || read/post 权限 见 permissions.h: PERM_*

with lib :
     set_up_new_board

#    It seems that count(*) in InnoDB is slow.
#    http://www.cloudspace.com/blog/2009/08/06/fast-mysql-innodb-count-really-fast/

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
            return None

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
        post['bid'] = self['bid']
        kv_pairs = post.dump_attr()
        exist_attr = kv_pairs.keys()
        exist_val = map(lambda x : self.to_str(x) ,kv_pairs.values())
        sql = "INSERT INTO %s(%s) values(%s)" % (self.table, ','.join(exist_attr), ','.join(exist_val))
        print sql
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
        k_e_v = [str(k)+"="+self.to_str(v) for k,v in kv_pairs]
        sql = "UPDATE %s SET %s where pid = %s" % (self.table, ','.join(k_e_v), post['pid'] )
        self.execute(sql)

    def update_board(self, upattr = []):
        """
            Update board
            If upattr is not empty, WILL only update atttributes in upattr.
        """
        if self['bid'] == None:
            return -1
        if len( upattr ):
            kv_pairs = filter(lambda(k,v): k in upattr, self.dump_attr())
        else:
            kv_pairs = self.dump_attr()
        k_e_v = [str(k)+"="+self.to_str(v) for k,v in kv_pairs]
        sql = "UPDATE argo_boardhead SET %s where bid = %s" % (','.join(k_e_v), self['bid'] )
        self.execute(sql)

    def close(self):
        self.closedb()

    def dump_attr(self):
        return self.dict.copy()

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
        return self.dict.copy()

"""
    `uid` int(11) unsigned NOT NULL auto_increment,
    `userid` varchar(20) NOT NULL,
    `passwd` varchar(64), || md5密码 或者 用scrypt?
    `nickname` varchar(20),
    `email` varchar(80), || 注册时的email地址
    `userlevel` int(11) unsigned NOT NULL default 0,  || 用户权限，PERM_*
    `netid`  varchar(20), || 注册时的netid，新用户用netid验证
    `iconidx` varchar(20), || 头像的index，图片，文件等等都用index识别，不存数据库

    `firstlogin` datetime NOT NULL default '0000-00-00 00:00:00', || 注册时间
    `firsthost` varchar(20),  || 注册地点 ,ip
    `lastlogin` datetime NOT NULL default '0000-00-00 00:00:00', || 最后登录时间
    `lasthost` varchar(20), || 最后登录地点
    `lastlogout` datetime NOT NULL default '0000-00-00 00:00:00', || 最后登出时间
    `numlogins` int(11) unsigned default 1, || 登录次数
    `numposts` int(11) unsigned default 0, || 发贴数
    `credit` int(11) unsigned default 0, || 分数，用于标示该用户信誉（提倡发精华贴）
    `lastpost` datetime NOT NULL default '0000-00-00 00:00:00', || 最后发贴时间
    `stay` int(11) unsigned default 0, || 在线时间
    `life`  int(11) default 666, || 生命力， 每天-1, 0后自动清除
    `lastupdate` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP, || 这里的属性的最后更新时间

    `birthday` date NOT NULL default '1990-01-01', || 生日
    `address` varchar(50), || 通信地址
    `usertitle` varchar(20) NOT NULL default 'user', || 称号，ie。版主:bm, 管理员..
    `gender`  int(11) unsigned default 1, || 性别 0: M   1: F
    `realname` varchar(20), || 真实姓名

"""

class User(Model):

    table = 'argo_user'

    def __init__(self, userid):
        if userid == "": return None

        super(User, self).__init__()
        self.userid = self.escape_string(userid)
        if self.init_user_info() < 0:
            return None

    def init_user_info(self):

        sql = "SELECT * FROM %s WHERE userid = '%s'" % (self.table, self.userid)
        res = self.query(sql)
        """ select static attrs """
        if len(res) == 1:
            self.dict = self.escape_attr(res[0]) # escape None value
            return 0
        else:
            self.dict = {}
            return -1

        """ select dynamic attrs """
        sql = "SELECT attr FROM %s WHERE userid = '%s'" (self.table, self.userid)
        res = self.query(sql)
        if len(res):
            self.attr = cPickle.load(res['attr'])  # unpack from binary stream
        else:
            self.attr = {}

    def __getitem__(self, name):
        try:
            return self.dict[name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        self.dict[name] = value

    def dump_attr(self):
        return self.dict.items()

    def has_perm(self, perm):
        try:
            if (self['userlevel'] & perm) > 0: return True
            else: return False
        except KeyError:
            return False

    def update_user(self, upattr = []):
        """
            The same as update_board
            如果upattr不是空，则只更新upattr中的属性
        """
        pass

    def update_attr(self):
        """
            Update dynamic attr in argo_userattr
        """
        pass

    #  版面相关

    def has_bm_perm(self, board):
        """
            Check if self.userid in board.bm  'gcc:cypress:LTS'
        """
        pass

    def has_post_perm(self, board):
        """
            Todo: phpbbs/common/class-user.php : has_post_perm
        """
        pass

    def has_read_perm(self, board):
        """
            Todo: phpbbs/common/class-user.php : has_post_perm
        """
        pass

    # 用户操作相关

    def logout(self):
        pass

    def send_post(self, board, post):
        """
            if self.has_post_perm(board):
                board.add_post(post)
                self.numposts++;
                self.update_user(['numposts'])
        """
        pass

    def del_post(self, board, post):
        """
            先判权，如果是bm或者帖子作者则可以删
        """
        pass

    def get_mail_table(self):
        """
            暂时放一个表，以后再根据以下规则切表
            argo_mailhead_${self.uid % 100}
        """
        return 'argo_mailhead'

    def check_mail(self):
        """
            查是否有未读邮件
        """
        table = self.get_mail_table()
        sql = "SELECT count(*) as total FROM %s WHERE touserid = '%s' and readmark = 0" % (table, self.userid)
        res = self.query(sql)[0]
        return res['total']


    def send_mail(self, touserid, mailobj):
        """
            destuser.recv_mail(self.userid, mailobj)
        """
        table = self.get_mail_table()
        # more to code
        pass

"""

    `mid` int(11) unsigned NOT NULL auto_increment, || mailid ,uinque
    `fromuserid` varchar(14) NOT NULL, || 发信人
    `touserid` varchar(14) NOT NULL, || 收信人
    `attachidx` varchar(20), || 站内信可以带附件！！

    `sendtime` int(11) unsigned NOT NULL default 0, || 发信时间
    `fromaddr` varchar(64), || 发信的ip（如果没设置隐藏ip则显示之）

    `readmark` int(11) unsigned NOT NULL default 0, ||  0未读，1已读, 2已回复
    `content` text,
    `quote` text,
    `signature` text,

     mail和帖子一样，需要切表，暂时实现放一个表中
"""

class Mail(Model):
    """
        Mail, the same as Post
    """
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

class DataBase(Model):

    with open(config.SQL_TPL_DIR+'template/argo_filehead.sql') as f :
        board_template = f.read()

    def __init__(self):
        super(DataBase,self).__init__()
        self.set_up_section()
        # self.set_up_board()

    def init_database(self):
        for table_name in config.BASE_TABLE :
            with open(config.SQL_TPL_DIR+'argo_'+table_name+'.sql') as f:
                sql = f.read()
                self.execute(sql)

    def set_up_section(self):
        res = self.query("SELECT sectionname FROM argo_sectionhead")
        self.section = dict(map(lambda x : (x["sectionname"],Section(x["sectionname"])),res))

    def get_section(self,sectionname):
        return self.section[sectionname]

    def get_all_section(self):
        sql = 'SELECT * FROM argo_sectionhead'
        return self.query(sql)

    def del_section(self,sectionname):
        sql = "DELETE FROM argo_sectionhead WHERE sectionname = '%s'" % sectionname
        self.execute(sql)

    def get_board(self,boardname):
        return Board(boardname)

    def get_user(self,userid):
        return User(userid)

    def add_board(self,boardname,section,keys):
        keys['boardname'] = boardname
        print self.section
        keys['sid'] = self.section[section]['sid']
        sql = self.board_template % { "boardname" : boardname.encode('utf8')}
        self.execute(sql)
        self.insert_dict('argo_boardhead',keys)

    def add_section(self,sectionname,keys):
        keys['sectionname'] = sectionname
        self.insert_dict('argo_sectionhead',keys)

    @staticmethod
    def _encrypt(passwd):
        from hashlib import md5
        m = md5()
        m.update(passwd)
        return m.hexdigest()

    def check_user_exist(self,userid):
        sql = "SELECT userid FROM argo_user WHERE userid = '%s'" % userid
        res = self.query(sql)
        return len(res)

    def add_user(self,username,passwd,keys):
        keys['userid'] = username
        keys['passwd'] = self._encrypt(passwd)
        self.insert_dict('argo_user',keys)

    def login(self,userid, passwd):
        res = self.query("SELECT userid FROM argo_user WHERE userid = '%s' and passwd = '%s' " % ( userid, self._encrypt(passwd)))
        if len(res) == 1 : return User(userid)
        else : return None

db_orm = DataBase()
