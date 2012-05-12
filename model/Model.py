# -*- coding: utf-8 -*-

from string import Template
import time
import bcrypt
import dbapi
from globaldb import global_conn, global_cache

class AuthError(Exception):pass

class Model(object):

    cache_prefix = 'argo_'

    def __init__(self):
        self.db = global_conn
        self.cache = global_cache

    def __getitem__(self, name):
        try:
            return self.dict[name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        self.dict[name] = value

    def escape_string(self, rawsql):
        if type(rawsql) != type(''):
            return rawsql
        safe_sql = self.db.escape_string(rawsql)
        return safe_sql

    def query(self, sql, params = ()):
        params = map(self.escape_string, params)
        res = self.db.query(sql % tuple(params))
        # print 'DEBUG: sql %s %d' % (sql,len(res))
        return res

    def query_noescape(self, sql, params = ()):
        res = self.db.query(sql % tuple(params))
        return res

    def execute(self, sql, params = ()):
        params = map(self.escape_string, params)
        self.db.execute(sql % tuple(params))

    def execute_noescape(self, sql, params = ()):
        self.db.execute(sql % params)

    def escape_attr(self, dict):
        res = {}
        for k,v in dict.items():
            if v != None:
                res[k] = v
        return res

    def insert_dict(self,table,kv_pairs):
        exist_attr = kv_pairs.keys()
        exist_val = map(lambda x : self.to_str(self.escape_string(x)),kv_pairs.values())
        self.execute_noescape("INSERT INTO %s(%s) values(%s)" , (table, ','.join(exist_attr), ','.join(exist_val)))

    def to_str(self, s):
        return "'%s'" % s;

    def close():
        self.db.close()

    def dump_attr(self):
        pass

    # cache relate functions

    def gen_key(self, key):
        '''
            Just add argo_ as key prefix
        '''
        return self.cache_prefix + key

    def set_add(self, key, value):
        key = self.gen_key(key)
        return self.cache.sadd(key, value)

    def set_card(self, key):
        key = self.gen_key(key)
        return self.cache.scard(key)

    def set_members(self, key):
        key = self.gen_key(key)
        return self.cache.smembers(key)

    def set_rem(self, key):
        key = self.gen_key(key)
        return self.cache.srem(key)

    def hash_set(self, key, field, value):
        key = self.gen_key(key)
        print key,field, value
        return self.cache.hset(key, field, value)

    def hash_get(self, key, field):
        key = self.gen_key(key)
        return self.cache.hget(key, field)

    def hash_mset(self, key, dict):
        key = self.gen_key(key)
        return self.cache.hmset(key, dict)

    def hash_delall(self, key):
        key = self.gen_key(key)
        hash_fields = self.cache.hkeys(key)
        for f in hash_fields:
            self.cache.hdel(key, f)

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
        res = self.query("SELECT * FROM argo_sectionhead where sectionname='%s'" , (self.sectionname,))

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
        return self.dict.copy()

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

    May change to MyISAM for performance.
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
        self.insert_dict(self.table , post.dict)

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
        return self.dict.items()

    def dump_attr_dict(self):
        return self.dict.copy()

    ### Cache

    def user_enter(self,userid):
        userid = self.escape_string(userid)
        self.set_add(self['boardname'] + '_online_userid',userid)
        
    def count_online(self):
        return self.set_card(self['boardname'] + '_online_userid')

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

    user_prefix = 'user:'

    '''
		用户状态属性的hashkey例子： argo_user:gcc
        用redis的hash，不同的field存不同的动态属性，
        如:
        1) 最后活跃时间last_active
        2) 所处模式mode(登录/文笔挥毫/信笺/etc)
        3) 即时消息
        etc...
	'''

    def __init__(self, userid = 'guest'):

        super(User, self).__init__()
        self.userid = self.escape_string(userid)

        if userid != 'guest' and self.init_user_info() < 0:
            return None

    def __getitem__(self, name):
        try:
            return self.dict[name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        self.dict[name] = value

    def init_user_info(self):

        sql = "SELECT * FROM %s WHERE userid = '%s'" % (self.table, self.userid)
        res = self.query(sql)
        if len(res) == 0:
            self.dict = {}
            return -1

        self.dict = self.escape_attr(res[0]) # escape None value
        # load dynamic attrs from blob
        if self.dict.has_key('attr'):
            self.dict.attr = cPickle.loads(self.dict.attr)

        self.mail_table = self.get_mail_table()
        self.cache_key = self.get_cache_key()

        # set last active time into cache
        # in order to kick those inactive user
        self.hash_set(self.cache_key, 'last_active', time.time() )
        return 0

    def get_cache_key(self):

        return self.user_prefix + self.userid

    def dump_attr(self):
        return self.dict.copy()

    def update_dict(self,new_dict):
        self.dict.update(new_dict)

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
        if not upattr : pass # todo
        sql_value = [ "%s = '%s'" % (key,self[key]) for key in upattr ]
        sql = "UPDATE argo_user SET %s WHERE uid = '%s'" %\
            (','.join(sql_value),self['uid'])
        self.execute(sql)

    def set_passwd(self,passwd):
        sql = "UPDATE argo_user SET passwd = '%s' WHERE uid = '%s'" % (self._encrypt(passwd),self['uid'])
        self.execute(sql)

    def update_attr(self):
        """
            Update dynamic attr
        """
        pickattr = cPickle.dumps(self.dict.dattr, 2)
        self.execute("UPDATE %s SET dattr = '%s' WHERE userid = '%s'", (self.table, pickattr, self.userid))

    #  版面相关

    def has_bm_perm(self, board):
        """
            Check if self.userid in board.bm  'gcc:cypress:LTS'
        """
        bms = board['bm'].split(':')
        if self.userid in bms: return True
        else: return False

    def has_post_perm(self, board):
        """
            Todo: phpbbs/common/class-user.php : has_post_perm
        """
        return True

    def has_read_perm(self, board):
        """
            Todo: phpbbs/common/class-user.php : has_read_perm
        """
        return True

    # 用户操作相关

    #@staticmethod
    #def login(userid, passwd):
    #    res = "SELECT * FROM %s WHERE userid = '%s' and passwd = '%s' " % (self.table, userid, passwd)
    #    if len(res) == 1 : return User(userid)
    #    else : return None

    def logout(self):
        self.set_rem(self.dict['userid'])
        self.hash_delall(self.cache_key)

    def send_post(self, board, post):
        """
            if self.has_post_perm(board):
                board.add_post(post)
                self.numposts++;
                self.update_user(['numposts'])
        """
        if not self.has_post_perm(board): return False
        board.add_post(post)
        self['numposts'] += 1
        self.update_user(['numposts'])

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
        sql = "SELECT count(*) as total FROM %s WHERE touserid = '%s' and readmark = 0" % (self.mail_table, self.userid)
        res = self.query(sql)[0]
        return res['total']

    def send_mail(self, touserid, mailobj):
        """
            destuser.recv_mail(self.userid, mailobj)
        """
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
        return self.dict.copy()

class DataBase(Model):

    def __init__(self):
        super(DataBase,self).__init__()
        self.set_up_section()
        # self.set_up_board()

    def init_database(self):
        import config
        for table_name in config.BASE_TABLE :
            with open(config.SQL_TPL_DIR+'argo_'+table_name+'.sql') as f:
                sql = f.read()
                self.execute(sql)

    def set_up_section(self):
        res = self.query("SELECT sectionname FROM argo_sectionhead")
        self.sections = dict(map(lambda x : (x["sectionname"],Section(x["sectionname"])),res))

    def get_section(self,sectionname):
        return self.sections[sectionname]

    def get_all_section(self):
        return self.sections

    def get_board(self,boardname):
        return Board(boardname)

    def get_boards(self,section_name): 
        if section_name in self.sections :
            sid = self.sections[section_name]['sid']
            sql = "SELECT boardname FROM argo_boardhead WHERE sid = %d" % sid
            res = self.db.query(sql)
            return [Board(b['boardname']) for b in res]

    def get_user(self,userid):
        return User(userid)

    def add_board(self, boardname, sid, keys):

        with open('database/template/argo_filehead.sql') as f :
            board_template = Template(f.read())

        keys['sid'] = sid
        keys['boardname'] = boardname
        self.execute(board_template.safe_substitute({'boardname' : boardname}))
        self.insert_dict('argo_boardhead',keys)

    def add_section(self,sectionname,keys):
        keys['sectionname'] = sectionname
        self.insert_dict('argo_sectionhead',keys)

    '''  User relate functions '''

    def add_user(self,username,passwd,keys):
        keys['userid'] = username

        # Use bcrypt now
        keys['passwd'] = bcrypt.hashpw(passwd, bcrypt.gensalt())

        self.insert_dict('argo_user',keys)

    def check_passwd(self, userid, passwd):

        res = self.query("SELECT passwd FROM argo_user WHERE userid = '%s'" , (userid,))
        if len(res) == 0: return False

        code = res[0]['passwd']

        if bcrypt.hashpw(passwd, code) == code:
            return True
        else:
            return False

    def check_user_not_exist(self, userid):
        userid = self.escape_string(userid)
        res = self.query("SELECT userid FROM argo_user WHERE userid = '%s'" ,  (userid,))
        print res
        if len(res) == 0 :
            return True
        return False

    def login(self, userid, passwd):
        userid = self.escape_string(userid)
        if not self.check_passwd(userid, passwd):
            return None

        self.set_add('online_userid', userid)
        print self.set_card('online_userid')

        u = User(userid)

        return u

    def login_guest(self):
        pass

    def total_online(self):
        '''
            返回online_userid  set中的元素个数，即在线人数
        '''
        return self.set_card('online_userid')

    def get_online_users(self):
        '''
            返回所有在线用户userid list
        '''
        return self.set_members('online_userid')

db_orm = DataBase()
