#!/usr/bin/python2
# -*- coding: utf-8 -*-

from globaldb import global_conn,global_cache
from MySQLdb import ProgrammingError
from error import *
import bcrypt,time
from datetime import datetime
import mode
import random
# import perm
import logging

logger = logging.getLogger('model')

class MetaModel(type):

    all_model = []

    def __new__(cls,names,bases,attrs):
        old_cls = cls
        cls = super(MetaModel,cls).__new__(cls,names,bases,attrs)
        if attrs.get('__clsinit__') is not None:
            cls.__clsinit__(names,bases,attrs,old_cls)
        cls.__modelname__ = names
        old_cls.all_model.append(cls)
        return cls

class Cacher:

    def __init__(self,name,ch = None):
        self.__ = name
        self.ch = ch

    def hmset(self,dic):
        return self.ch.hmset(self.__, dic)

    def hlen(self):
        return self.ch.hlen(self.__)

    def hget(self,field):
        return self.ch.hget(self.__, field)

    def hincrby(self,field,amount=1):
        return self.ch.hincrby(self.__, field, amount)

    def hdel(self,field):
        return self.ch.hdel(self.__, field)
        
def v__(s,*args):
    # try:
    print s % args
    # except:
    print '*' * 20
    print s
    print args
    return (s,) + args

class Model:
    
    u'''
    A base class for a model. It implemented some common methods as well.
    Basic useage read the Manage class.
    '''
    
    __metaclass__ = MetaModel

    def __init__(self):
        self.dict = {}
    
    def bind(self,db=None,ch=None):
        if db : self.db = db
        if ch : self.ch = ch

    def configure(self):
        pass

    def table_select_all(self,tablename):
        return self.db.query("SELECT * FROM `%s`" % tablename)

    def table_get_by_key(self,tablename,key,value):
        return self.db.get("SELECT * FROM `%s` WHERE %s = %%s" %\
                               (tablename,key),
                           value)

    def execute_paragraph(self, para):
        self.db.execute_paragraph(para)

    def table_insert(self,tablename,attr):
        names,values = zip(*attr.items())
        cols = ','.join(map(str,names))
        vals = ','.join(('%s',) * len(values))
        return self.db.execute("INSERT INTO `%s` (%s) VALUES (%s)" % \
                                   (tablename, cols,vals),
                               *values)
    
    def table_update_by_key(self,tablename,key,value,attr):
        names,values = zip(*attr.items())
        set_sql = ','.join( map(lambda x: "%s = %%s" % x,names))
        return self.db.execute("UPDATE `%s` SET %s WHERE %s = %%s" % \
                                   (tablename, set_sql, key),
                               *(values + (value,)))

    def table_delete_by_key(self,tablename,key,value):
        return self.db.execute("DELETE FROM `%s` WHERE %s = %%s" % \
                                   (tablename, key),
                               value)

    def table_select_by_key(self,tablename,what,key,value):
        return self.db.get("SELECT %s FROM `%s` WHERE %s = %%s" %\
                               (what, tablename, key),
                           value)

    def table_get_listattr(self, tablename, what, key, value):
        res = self.db.get("SELECT %s FROM `%s` WHERE %s=%%s"%(what, tablename, key),
                          value)
        return res and ( (res[what] and res[what].split(':')) or [])

    def table_update_listattr(self, tablename, what, listattr, key, value):
        r = ':'.join(listattr)
        return self.db.execute("UPDATE `%s` SET %s=%%s WHERE %s=%%s" % \
                                   (tablename, what, key),
                               r, value)

    def u(self, char):
        return char.decode('utf-8')        

    def _wrapper_index(self, data, num):
        for index in range(len(data)):
            data[index]['index'] = num + index
        return data

class Section(Model):

    u'''
    The module of sections opeartor. It's almost all deal with the
    `argo_sectionhead` table in SQL database.

    db: argo_sectionhead
    '''

    __ = 'argo_sectionhead'

    def get_all_section(self):
        return self.table_select_all(self.__)

    def get_all_section_with_rownum(self):
        d = self.get_all_section()
        return with_index(d)

    def get_section(self,name):
        u''' Get a section by sectionname.'''
        return self.table_get_by_key(self.__, 'sectionname', name)

    def get_section_by_sid(self, sid):
        return self.table_get_by_key(self.__, 'sid', sid)

    def add_section(self,**kwargs):
        return self.table_insert(self.__, kwargs)
    
    def update_section(self, sid, **attr):
        return self.table_update_by_key(self.__, 'sid', sid, attr)
    
    def del_section(self,sid):
        return self.table_delete_by_key(self.__, 'sid', sid)
    
    def name2id(self,sectionname):
        d = self.table_select_by_key(self.__, 'sid', 'sectionname', sectionname)
        return d and d['sid']

    def id2name(self,sid):
        n = self.table_select_by_key(self.__, 'sectionname', 'sid', sid)
        return n and n['sectionname']

    def get_max_sid(self):
        n = self.db.get("SELECT max(sid) FROM %s" % self.__)
        return n or 0
        
class Board(Model):

    u'''
    The low level operation of boards. It just wrap up some opearator
    with SQL database.
    The recommend board was implemented here.

    db:argo_boardhead
       argo_recommend    
    '''

    __ = 'argo_boardhead'
    _r = 'argo_recommend'
    
    def get_by_sid(self,sid):
        return self.db.query("SELECT * FROM `%s` WHERE sid = %%s" % self.__,
                             sid)

    def get_all_boards(self):
        return self.table_select_all(self.__)

    def get_board(self,name):
        return self.table_get_by_key(self.__, 'boardname', name)

    def get_recommend(self):
        return self.db.query(
            "SELECT %s.* FROM `%s` INNER JOIN %s ON "
            "%s.bid = %s.bid ORDER BY %s.bid" % \
                (self.__, self.__, self._r, self.__, self._r, self.__))

    def add_recommend(self,bid):
        return self.table_insert(self._r,  dict(bid=bid))

    def del_recommend(self,bid):
        return self.table_delete_by_key(self._r, 'bid', bid)

    def get_board_by_id(self,bid):
        return self.table_get_by_key(self.__, 'bid', bid)

    def add_board(self,**kwargs):
        return self.table_insert(self.__, kwargs)
    
    def update_board(self,bid,**attr):
        return self.table_update_by_key(self.__, 'bid', bid, attr)
    
    def del_board(self,bid):
        return self.table_delete_by_key(self.__, 'bid', bid)
    
    def name2id(self,boardname):
        logger.debug('name2id -- %s',boardname)
        d = self.table_select_by_key(self.__, 'bid', 'boardname', boardname)
        return d and d['bid']
    
    def id2name(self,bid):
        d = self.table_select_by_key(self.__, 'boardname', 'bid', bid)
        return d and d['boardname']

    def update_attr_plus1(self,bid,key):
        return self.db.execute("UPDATE %s SET %s = %s +1 WHERE bid = %%s" % \
                                   (self.__, key, key),
                               bid)

    def get_board_bm(self, boardname):
        return self.table_get_listattr(self.__,  'bm', 'boardname', boardname)

    def set_board_bm(self, boardname, bms):
        return self.table_update_listattr(self.__, 'bm', bms, 'boardname', boardname)

class Favourite(Model):

    u'''
    low level operation of user favourite.

    ch:
        {set} argo:favourite:$userid
    '''

    keyf = "argo:favourite:%s"
    default_userid = '+default+'

    def init_user_favourite(self, userid):
        key = self.keyf % userid
        self.ch.delete(key)
        self.ch.sunionstore(key, self.keyf % self.default_userid)

    def add(self, userid, boardname):
        u''' Add an board into user's favourtie.'''
        key = self.keyf % userid
        self.ch.sadd(key, boardname)
                      
    def remove(self, userid, boardname):
        key = self.keyf % userid
        self.ch.srem(key, boardname)

    def get_all(self, userid):
        u'''Return a set holds all board's name in user's favourte.'''
        key = self.keyf % userid
        return self.ch.smembers(key)

    def add_default(self, boardname):
        self.add(self.default_userid, boardname)

    def remove_default(self, boardname):
        self.remove(self.default_userid, boardname)

class Post(Model):

    u'''
    Low level operation of post.

    db: argo_filehead_$boardname
    ch: [hash] : argo_lastpost[boardname]
    
    '''

    _prefix = 'argo_filehead_%s'
    _table_junk = 'argo_filehead_%s_junk'
    _person_junk = 'argo_filehead_JUNK'
    
    lastp = 'argo:lastpost'

    all_attrs = ['pid', 'bid' ,'owner' ,'realowner' ,'title' ,'flag' ,
                 'tid' ,'replyid' ,'posttime' ,'attachidx' ,'fromaddr' ,
                 'fromhost' ,'content' ,'quote' ,'signature' ,'agree' ,
                 'disagree' ,'credit' ,'originalfilename' ,'replyable']

    all_attrs_str = ','.join(all_attrs)
    
    def __(self,boardname):
        return self._prefix % boardname

    def _get_junk_table(self, boardname):
        return self._table_junk % boardname        

    def _create_table(self,boardname,**kwargs):
        import config
        from string import Template
        with open(config.SQL_TPL_DIR + 'template/argo_filehead.sql') as f :
            board_template = Template(f.read())
            self.execute_paragraph(board_template.safe_substitute(
                    boardname=boardname))

    def _create_table_junk(self, boardname, **kwargs):
        import config
        from string import Template
        with open(config.SQL_TPL_DIR + 'template/argo_filehead_junk.sql') as f :
            board_template = Template(f.read())
            self.execute_paragraph(board_template.safe_substitute(
                    boardname=boardname))

    def _move_post(self, tablename, pid, new_tablename):
        self.db.execute("INSERT INTO `%s` (%s) "
                        "SELECT %s "
                        "FROM `%s` "
                        "WHERE pid=%%s" % (new_tablename, self.all_attrs_str,
                                           self.all_attrs_str, tablename),
                        pid)
        return self.db.execute("DELETE FROM %s "
                               "WHERE pid=%%s" % tablename, pid)

    def _move_post_range(self, tablename, new_tablename, start, end):
        self.db.execute("INSERT INTO `%s` (%s) "
                        "SELECT %s "
                        "FROM `%s` "
                        "WHERE pid>=%%s AND pid<%%s AND not flag" % \
                            (new_tablename, self.all_attrs_str,
                             self.all_attrs_str, tablename),
                        start, end)
        return self.db.execute("DELETE FROM %s "
                               "WHERE pid>=%%s AND pid<%%s AND not flag" % tablename, start, end)

    def _move_post_many(self, tablename, new_tablename, pids):
        self.db.executemany("INSERT INTO `%s` (%s) "
                            "SELECT %s "
                            "FROM `%s` "
                            "WHERE pid=%%s AND not flag" % (new_tablename, self.all_attrs_str,
                                                            self.all_attrs_str, tablename),
                            pids)
        return self.db.executemany("DELETE FROM %s "
                                   "WHERE pid=%%s AND not flag" % tablename, pids)

    def remove_post_junk(self, boardname, pid):
        return self._move_post(self.__(boardname), pid,
                               self._get_junk_table(boardname))

    def remove_post_junk_range(self, boardname, start, end):
        return self._move_post_range(self.__(boardname), self._get_junk_table(boardname),
                                     start, end)

    def remove_post_personal(self, boardname, pid):
        return self._move_post(self.__(boardname), pid,
                               self._person_junk)

    def get_junk_posts(self, boardname, num, limit):
        return self.db.query("SELECT * FROM `%s` ORDER BY jid LIMIT %%s,%%s" % \
                                 self._get_junk_table(boardname), num, limit)

    def get_personal_junk(self, boardname, author):
        return self.db.query("SELECT * FROM `%s` WHERE owner=%s" % \
                                 self._person_junk,  author)

    def clear_personal_junk(self):
        return self.db.execute("TRUNCATE TABLE %s" % self._person_junk)

    def _wrapper_index(self, data, num):
        for index in range(len(data)):
            data[index]['index'] = num + index
        return data

    def get_rank_num(self, boardname, pid):
        return self.db.get('SELECT count(*) '
                           'FROM `%s` '
                           'WHERE pid<%%s '
                           'ORDER BY pid' % self.__(boardname),
                           pid)['count(*)']

    def get_rank_num_cond(self, boardname, pid, cond):
        return self.db.get('SELECT count(*) '
                           'FROM `%s` '
                           'WHERE pid<%%s AND %s '
                           'ORDER BY pid' % (self.__(boardname), cond),
                           pid)['count(*)']

    #####################

    FILTER_G = 'flag & 1'
    FILTER_M = 'flag & 2'
    FILTER_O = 'replyid=0'

    def sql_filter_tid(self, tid):
        return 'tid=%s' % self.db.escape_string(str(tid))

    def sql_filter_owner(self, owner):
        return 'tid=%s' % self.db.escape_string(owner)

    def sql_and(self,buf):
        return ' AND '.join(buf)

    def get_posts(self, boardname, num, limit):
        res = self.db.query("SELECT * FROM `%s` ORDER BY pid LIMIT %%s,%%s" %\
                            self.__(boardname), num, limit)
        return self._wrapper_index(res, num)

    def get_posts_loader(self, boardname, cond=''):
        if cond :
            sql = "SELECT * FROM `%s` WHERE %s ORDER BY pid LIMIT %%s,%%s" % \
                (self.__(boardname), cond)
        else:
            sql = "SELECT * FROM `%s` ORDER BY pid LIMIT %%s,%%s" % \
                self.__(boardname)
        return lambda start, limit: self._wrapper_index(
            self.db.query(sql, start, limit), start,
            )

    def get_posts_counter(self, boardname, cond=''):
        if cond :
            sql = "SELECT count(*) FROM `%s` WHERE %s" % \
                (self.__(boardname), cond)
        else:
            sql = "SELECT count(*) FROM `%s`" % self.__(boardname)
        return lambda : self.db.get(sql)['count(*)']
        
    def get_posts_total(self, boardname):
        return self.db.get("SELECT count(*) FROM %s" % self.__(boardname))['count(*)']

    def get_posts_g(self,boardname,num,limit):
        res = self.db.query("SELECT * FROM `%s` WHERE flag & 1 ORDER BY pid LIMIT %%s,%%s" %\
                                self.__(boardname), num, limit)
        return self._wrapper_index(res, num)

    def get_posts_g_total(self, boardname):
        return self.db.get("SELECT count(*) FROM %s WHERE flag & 1" % self.__(boardname))['count(*)']

    def get_posts_m(self,boardname,num,limit):
        res = self.db.query("SELECT * FROM `%s` WHERE flag & 2 ORDER BY pid LIMIT %%s,%%s" %\
                                       self.__(boardname), num, limit)
        return self._wrapper_index(res, num)

    def get_posts_m_total(self, boardname):
        return self.db.get("SELECT count(*) FROM %s WHERE flag & 2" % self.__(boardname))['count(*)']
    
    def get_posts_topic(self,boardname,num,limit):
        res = self.db.query("SELECT * FROM `%s` WHERE replyid=0 ORDER BY pid LIMIT %%s,%%s" %\
                                self.__(boardname), num, limit)
        return self._wrapper_index(res, num)

    def get_posts_topic_total(self, boardname):
        return self.db.get("SELECT count(*) FROM %s WHERE replyid=0" % self.__(boardname))['count(*)']

    def get_posts_onetopic(self,tid,boardname,num,limit):
        res = self.db.query("SELECT * FROM `%s` WHERE tid=%%s ORDER BY pid LIMIT %%s,%%s" %\
                                self.__(boardname), tid, num, limit)
        return self._wrapper_index(res, num)

    def get_posts_onetopic_total(self, tid, boardname):
        return self.db.get("SELECT count(*) FROM %s WHERE tid=%%s" % self.__(boardname), tid)['count(*)']

    def get_posts_owner(self,author,boardname,num,limit):
        res = self.db.query("SELECT * FROM `%s` WHERE owner=%%s ORDER BY pid LIMIT %%s,%%s" %\
                                self.__(boardname), author, num, limit)
        return self._wrapper_index(res, num)

    def get_posts_owner_total(self, author, boardname):
        return self.db.get("SELECT count(*) FROM %s WHERE owner=%s" % self.__(boardname), author)['count(*)']

    ####################

    def get_last_pid(self,boardname):
        return self.ch.hget(self.lastp, boardname) 
        # res = self.db.get("SELECT pid FROM `%s` ORDER BY pid DESC LIMIT 1" % \
        #                       self.__(boardname))
        # return res and res['pid']

    def get_post_loader(self, boardname):
        sql_next = "SELECT * FROM `%s` WHERE pid > %%s ORDER BY pid LIMIT 1" % self.__(boardname)
        sql_prev = "SELECT * FROM `%s` WHERE pid < %%s ORDER BY pid DESC LIMIT 1" % self.__(boardname)
        fun = self.db.get
        return (lambda pid : fun(sql_next, pid),
                lambda pid : fun(sql_prev, pid))

    def get_topic_post_loader(self, boardname, tid):
        assert isinstance(tid, long)
        sql_next = "SELECT * FROM `%s` WHERE pid > %%s AND tid=%s ORDER BY pid LIMIT 1" % (self.__(boardname), tid)
        sql_prev = "SELECT * FROM `%s` WHERE pid < %%s AND tid=%s ORDER BY pid DESC LIMIT 1" % (self.__(boardname), tid)
        fun = self.db.get
        return (lambda pid : fun(sql_next, pid),
                lambda pid : fun(sql_prev, pid))

    def get_post(self,boardname,pid):
        return self.table_get_by_key(self.__(boardname), 'pid', pid)

    def prev_post(self, boardname, pid):
        return self.db.get("SELECT * FROM `%s` WHERE pid < %%s ORDER BY pid DESC LIMIT 1"%\
                               self.__(boardname), pid)

    def next_post(self, boardname, pid):
        return self.db.get("SELECT * FROM `%s` WHERE pid > %%s ORDER BY pid LIMIT 1" %\
                               self.__(boardname), pid)

    def prev_post_pid(self,boardname,pid):
        res = self.db.get("SELECT pid FROM `%s` WHERE pid < %%s ORDER BY pid DESC LIMIT 1" %\
                              self.__(boardname), pid)
        return res and res['pid']

    def next_post_pid(self,boardname,pid):
        res = self.db.get("SELECT pid FROM `%s` WHERE pid > %%s ORDER BY pid LIMIT 1" %\
                              (self.__(boardname),pid))
        return res and res['pid']

    def add_post(self,boardname,**kwargs):
        pid = self.table_insert(self.__(boardname), kwargs)
        self.ch.hset(self.lastp, boardname, pid)               ###############
        return pid

    def update_post(self,boardname,pid,**kwargs):
        return self.table_update_by_key(self.__(boardname), 'pid', pid, kwargs)

    def del_post(self,*args,**kwargs):
        u'''
        Never delete a post.
        '''
        pass

    def get_board_total(self,boardname):
        res = self.db.get("SELECT count(pid) as total FROM `%s`" % self.__(boardname))
        r = res.get('total')
        return (r and int(r)) or 0

    def update_title(self,boardname,pid,new_title):
        return self.update_post(boardname,pid,title=new_title)

    def pid2tid(self,boardname,pid):
        res = self.table_select_by_key(self.__(boardname),
                                       'tid','pid',pid)
        return res and res['tid']

    def pid2title(self,boardname,pid):
        res = self.table_select_by_key(self.__(boardname),
                                       'title','pid',pid)
        return res and res['title']

    def index2pid(self, boardname, index):
        if index <=0 : return 0
        res = self.db.get("SELECT pid FROM `%s` ORDER BY pid LIMIT %%s,1" % self.__(boardname),
                          index)
        if res :
            return res['pid']
        else:
            return self.get_last_pid(boardname) +1 

class UserInfo(Model):

    u'''
    Low level operation of user's info.
    db: argo_user
    '''

    __ = 'argo_user'

    def get_user(self,name):
        return self.table_get_by_key(self.__, 'userid', name)

    def add_user(self,**kwargs):
        return self.table_insert(self.__, kwargs)

    def update_user(self,userid,**kwargs):
        return self.table_update_by_key(self.__, 'userid', userid, kwargs)

    def del_user(self,userid):
        u'''
        Never delete a user.
        '''
        pass

    def name2id(self,userid):
        u'''
        Check if the userid is in database. Return the uid if so,
        or None if not.
        '''
        d = self.table_select_by_key(self.__, 'uid', 'userid', userid)
        return d and d['uid']

    def select_attr(self,userid,sql_what):
        return self.db.get("SELECT %s FROM `%s` WHERE userid = %%s" % (sql_what, self.__),
                           userid)

    def user_exist(self, userid):
        return True

class Status(Model):

    u'''
    The module include some action about online status record.

    Each connection has a unique (userid,sessionid) pair.
    
    Every login should first call the login() method to update
    amount of the online , and it will return a number as the
    sessionsid. After logout, logout() should be called to
    clear this.

    Every *session* has a status to holds the online status,
    set_status , get_status, clear_status are about this.
    
    When it's enter/exit a board, enter_board/exit_board should
    be called.

    ch :

       {string} argo:status_count :: next_sessionid

       {hash} argo:status_ip[sessionid] | primary ==> session's remote ip

       {hash} argo:status_userid[sessionid] ==> userid
       {hash} argo:status_status[sessionid] ==> status 

       {hash} argo:status_boardonline[boardname] ==> total_num in board

       {set} argo:status_user_session[userid] ==> user's sessionid

       {order map }
          argo:status_map[rank_score] ==> session id
    '''

    max_login = 9999

    _count = 'argo:status_count'
    _ip = 'argo:status_ip'
    _status = 'argo:status_status'
    _userid = 'argo:status_userid'
    _boardonline = 'argo:status_boardonline'
    _user_session = 'argo:status_user_session:%s'
    _map = 'argo:status_map'
    
    def new_session(self, remote, userid, status, rank_score):
        sessionid = self.ch.incr(self._count)
        self.ch.hset(self._ip, sessionid, remote)
        self.ch.hset(self._status, sessionid, status)
        self.ch.hset(self._userid, sessionid, userid)
        self.ch.sadd(self._user_session % userid, sessionid)
        self.ch.zadd(self._map, sessionid, rank_score)
        return sessionid

    def logout(self, sessionid):
        self.ch.hdel(self._status, sessionid)
        userid = self.ch.hget(self._userid, sessionid)
        self.ch.hdel(self._userid, sessionid)
        self.ch.srem(self._user_session % userid, sessionid)
        self.ch.zrem(self._map, sessionid)
        self.ch.hdel(self._ip, sessionid)

    def set_status(self, sessionid, status):
        return self.ch.hset(self._status, sessionid, status)

    def get_status(self, sessionid):
        return self.ch.hget(self._status, sessionid)

    def total_online(self):
        return self.ch.hlen(self._ip)

    def enter_board(self, boardname):
        self.ch.hincrby(self._boardonline, boardname)

    def exit_board(self, boardname):
        self.ch.hincrby(self._boardonline, boardname, -1)

    def board_online(self, boardname):
        return self.ch.hget(self._boardonline, boardname) or 0

    def get_rank(self, sessionid):
        return self.ch.zrank(self._map, sessionid)

    def get_session(self, sessionid):
        return dict(
            sessionid=sessionid,
            userid=self.ch.hget(self._userid, sessionid),
            status=self.ch.hget(self._status, sessionid),
            ip=self.ch.hget(self._ip, sessionid)
            )

    def get_sessionid_rank(self, start, limit):
        return self.ch.zrange(self._map, start, start+limit)

    def get_session_rank(self, start, limit):
        return map(self.get_session, self.get_sessionid_rank(start, limit))

    def clear_all(self):
        all_sesions = self.ch.hkeys(self._ip)
        for s in all_sesions:
            self.logout(s)
        self.ch.delete(self._boardonline)
            
class Mail(Model):

    u'''
    low level operation of mail.
    db: argo_mailhead_$groupid

    :groupid :: uid//100
    
    '''

    _prefix = 'argo_mailhead_'

    def __(self,uid):
        return self._prefix + str((int(uid) // 100))

    def _tableid(self,uid):
        return int(uid) / 100

    def _create_table(self,tableid):
        ###################################################################
        import config
        from string import Template
        with open(config.SQL_TPL_DIR + 'template/argo_mailhead.sql') as f :
            mail_template = Template(f.read())
            gentxt = mail_template.safe_substitute(tableid=tableid)
            self.execute_paragraph(gentxt)

    def send_mail(self, touid, **kwargs):
        try:
            return self.table_insert(self.__(touid), kwargs)
        except ProgrammingError as e:
            print e
            if e.args[0] == 1146 : # Table NOT EXIST
                self._create_table(self._tableid(touid))
                self.send_mail(touid, **kwargs)
            raise e

    def get_mail_loader(self, uid, userid):
        sql = "SELECT * FROM `%s` WHERE touserid=%%s ORDER BY mid LIMIT %%s, %%s" % (
            self.__(uid), self.escape_string(userid))
        func = self.db.query
        wrapper = self._wrapper_index
        return lambda o,l : wrapper(func(sql, o, l), o)

    def get_mail_counter(self, uid, userid):
        sql = "SELECT count(*) FROM `%s` WHERE touserid=%%s" % (
            self.__(uid), self.escape_string(userid))
        func = self.db.get
        return lambda : func(sql)['count(*)']

    def get_mail(self, touid, touserid, start, limit):
        try:
            return self.db.query("SELECT * FROM `%s` "
                                 "WHERE touserid=%%s "
                                 "ORDER BY mid "
                                 "LIMIT %%s,%%s" % (self.__(touid)), touserid,
                                 start, limit)
        except ProgrammingError as e:
            if e.args[0] == 1146 : # Table NOT EXIST
                self._create_table(self._tableid(touid))
                return []
            else:
                raise e

    def one_mail(self, touid, mid):
        return self.table_get_by_key(self.__(touid), 'mid', mid)
    
    def get_mail_total(self, touid, touserid):
        res = self.db.get("SELECT count(mid) as total FROM `%s` WHERE touserid = %%s" % self.__(touid), touserid)
        r = res.get('total')
        return int(r) if r else 0 

    def prev_mail(self, userid, touid, mid):
        return self.db.get("SELECT * FROM `%s` WHERE mid < %s ORDER BY mid DESC LIMIT 1" %\
                               (self.__(touid),mid))

    def next_mail(self, userid, touid, mid):
        return self.db.get("SELECT * FROM `%s` WHERE mid > %s ORDER BY mid LIMIT 1" %\
                               (self.__(touid),mid))

    # def get_new_mail(self, touid, touserid, num, limit):
    #     return self._query_mail(touid, touserid, limit, 'AND mid>=%s AND readmark = 0'%num)
    
    def get_last_mid(self, touid, touserid):
        res = self.db.get("SELECT max(mid) as maxid FROM `%s` WHERE touserid=%%s" % self.__(touid), touserid)
        r = res.get('maxid')
        return int(r) if r else 0 

    def del_mail(self,touid,mid):
        return self.table_delete_by_key(self.__(touid), 'mid',mid)

    def update_mail(self, uid, mid, **kwargs):
        return self.table_update_by_key(self.__(uid), 'mid', mid, kwargs)

    def set_read(self, uid, mid):
        sql = "UPDATE `%s` SET readmark = readmark | 1 WHERE mid = %%s" %\
            self.__(uid)
        self.db.execute(sql, mid)

    def set_reply(self, uid, mid):
        sql = "UPDATE `%s` SET readmark = readmark | 3 WHERE mid = %%s" %\
            self.__(uid)
        self.db.execute(sql, mid)

    def get_rank(self, userid, uid, mid):
        return self.db.get("SELECT count(*) FROM %s "
                           "WHERE mid<=%%s AND touserid=%%s" % self.__(uid),
                           mid, userid)['count(*)']

class Disgest(Model):

    u'''
    low level operation of disgest.
    db : argo_annhead_$boardname
    '''

    _prefix = 'argo_annhead_'

    def __(self, boardname):
        return self._prefix + boardname

    def _create_table(self, boardname, **kwargs):
        #################################
        import config
        from string import Template
        with open(config.SQL_TPL_DIR + 'template/argo_annhead.sql') as f :
            board_template = Template(f.read())
            self.execute_paragraph(board_template.substitute(boardname=boardname))

    def get_children(self, boardname, partent):
        return self.db.query("SELECT * FROM `%s` WHERE pid=%%s ORDER BY rank " % self.__(boardname),
                             partent)

    def get_node(self, boardname, nodeid):
        return self.db.get("SELECT * FROM `%s` WHERE id=%%s" % self.__(boardname),
                           nodeid)

    def get_children_and_tabs(self, boardname, partent):
        children = self.get_children(boardname, partent)
        for node in children:
            if node.title == 'README':
                return (children, node)
        else:
            return (children, None)

    def get_max_rank(self, boardname, partent):
        res = self.db.get("SELECT max(rank) FROM `%s` WHERE pid=%%s" % self.__(boardname),
                           partent)
        return res and (res['max(rank)'] or 0)

    def add_node_r(self, boardname, partent, rank, **kwargs):
        kwargs['pid'] = partent
        kwargs['rank'] = rank
        return self.table_insert(self.__(boardname), kwargs)

    def add_node(self, boardname, partent, **kwargs):
        rank = self.get_max_rank(boardname, partent) + 1
        return self.add_node_r(boardname, partent, rank, **kwargs)

    def delete_node(self, boardname, nodeid):
        return self.table_delete_by_key(self.__(boardname), 'id', nodeid)

    def swap_rank(self, boardname, node1, node2):
        r1 = node1.rank
        r2 = node2.rank
        sql = "UPDATE `%s` SET rank=%%s WHERE id=%%s" % self.__(boardname)
        return self.db.executemany(sql, ((r1, node2['id']), (r2, node1['id'])))

    def get_node_cc(self, srcboard, nodeid):
        return self.db.get("SELECT title,owner,flag,tags,content FROM %s WHERE id=%%s"%self.__(srcboard),
                           nodeid)

    # def walk_tree(self, boardname, nodeid):
    #     acc = []
    #     def walk(rootid):
    #         acc.append(rootid)
    #         children = self.db.get_children(boardname, rootid)
    #         for child in children :
    #             walk(child.id)
    #     walk(nodeid)
    #     return acc

    # def get_tree(self, boardname, node):
    #     def get_board_tree(node):
    #         if node.flag == 1:
    #             children = self.get_children(boardname, node['id'])
    #             children_tree = map(get_board_tree, children)
    #             return (node, children_tree)
    #         else:
    #             return (node, None)
    #     return get_board_tree(node)

    # def insert_tree(self, boardname, partentid, nodetree):
    #     node, children = nodetree
    #     res = self.add_node(boardname, partentid, **node)
    #     if children :
    #         for child in children:
    #             self.insert_tree(boardname, node['id'], child)
    #     return res

    # def delete_tree(self, boardname, nodeid):
    #     children = self.get_children(nodeid)
    #     if children:
    #         for child in children:
    #             self.delete_tree(boardname, child)
    #     self.delete_node(boardname, nodeid)

    # def copy_node(self, srcboard, nodeid, descboard, partentid, **kwargs):
    #     res = self.get_node_cc(srcboard, nodeid)
    #     res['rank'] = self.get_max_rank(self.__(descboard), partentid)
    #     res.update(kwargs)
    #     new_nodeid = self.table_insert(self.__(descboard), res)

    #     if res.flag == 1:
    #         for child in self.get_children(srcboard, nodeid):
    #             self.copy_node(srcboard, child.id,
    #                            descboard, new_nodeid)            
    #     else:
    #         return new_nodeid

class ReadMark(Model):

    u'''
    Implement the read/unread mark.
    It use a smart algorithm.

        https://github.com/argolab/argon/wiki/%E7%89%9BB%E9%97%AA%E9%97%AA%E7%9A%84%E6%9C%AA%E8%AF%BB%E6%A0%87%E8%AE%B0%E7%9A%84%E5%AE%9E%E7%8E%B0

    ch:  {order set} argo:readmark:%boardname:$userid [pid] ==> pid
    '''

    keyf = "argo:readmark:%s:%s"

    limit_max = 200
    limit_clear = -50

    def __(self,userid,boardname):
        return self.keyf%(userid,boardname)

    def __init__(self, post):
        self.post = post

    def is_read(self,userid,boardname,pid):
        key = self.keyf % (userid, boardname)
        # Empty record, not read
        # And play a trick here, add -1 into read mark
        if self.ch.zcard(key) == 0: 
            self.ch.zadd(key, -1, -1)
            return 0
        res = self.ch.zcount(key, pid, pid)
        if res: return res
        # If pid is smaller the oldest one in read record, mark as read
        first_pid = self.ch.zrange(key, 0, 0)[0]
        return pid < int(first_pid)

    def is_new_board(self,userid,boardname):
        lastpid = self.post.get_last_pid(boardname)
        return lastpid is not None and not self.is_read(userid, boardname, lastpid)

    def set_read(self,userid,boardname,pid):
        if self.is_read(userid, boardname, pid):
            return
        key = self.keyf%(userid,boardname)
        read_num = self.ch.zcard(key)
        if read_num >= self.limit_max:
            # Flush the oldest
            self.ch.zremrangebyrank(key, 0, self.limit_max - read_num )
        return self.ch.zadd(key,pid,pid)

    def clear_unread(self,userid,boardname,last):
        key = self.keyf%(userid,boardname)
        self.ch.delete(key)
        self.ch.zadd(key, last, last)

    def get_user_read(self, userid, boardname, num):
        return self.ch.zrange(self.__(userid, boardname),-num,-1)

class UserSign(Model):

    u'''
    About user's Signature File.
    ch : {list} argo:usersign:%userid
    '''

    keyf = "argo:usersign:%s"

    def set_sign(self,userid,data):
        assert all(map(lambda x :isinstance(x, unicode), data))
        key = self.keyf % userid
        if len(data) >= 20 :
            data = data[:20]
        self.ch.delete(key)
        self.ch.rpush(key,*data)

    def get_all_sign(self,userid):
        key = self.keyf % userid
        s = self.ch.lrange(key,0,-1)
        return map(self.u, s)

    def get_sign(self,userid,index):
        key = self.keyf % userid
        return self.u(self.ch.lindex(key,index))

    def get_random(self,userid):
        key = self.keyf % userid
        l = self.ch.llen(key)
        i = self.ch.lindex(key,random.randint(0,l-1))
        return self.u(self.ch.lindex(key,i))

    def get_sign_num(self,userid):
        key = self.keyf % userid
        return self.ch.llen(key)

class Team(Model):

    u'''
    About the team.

    ch : {set} argo:team_ust:$userid ==> team set
         {set} argo:team_tsm:$team ==> member set
    '''

    key_ust = 'argo:team_ust:%s' # User's team
    key_tsm = 'argo:team_tsm:%s' # Team's member

    key_name = 'argo:team_name'  # hash(key_name, teamid)  !! Primary
    key_mark = 'argo:team_all' # All Team, save a mark
    # key_owner = 'argo:team_owner' # hash(key_name, teamowner)
    key_publish = 'argo:team_publish'  # All the publish team
    
    # Base

    def all_team(self):
        return map(self.u, self.ch.hkeys(self.key_name))

    def register_team(self, teamid, teamname, publish):
        self.ch.hset(self.key_name, teamid, teamname)
        if publish :
            self.publish(teamid)

    def confirm_exists(self, teamid):
        if not self.exists(teamid):
            raise ValueError(u'No such team [%s]' % teamid)

    def drop_team(self, teamid):
        self.ch.hdel(self.key_name, teamid)
        self.ch.delete(self.key_ust % teamid)
        self.ch.delete(self.key_tsm % teamid)
        self.ch.hdel(self.key_mark, teamid)
        self.ch.publish(self.key_mark, teamid)

    def exists(self, teamid):
        return self.ch.hexists(self.key_name, teamid)

    def publish(self, teamid):
        self.ch.sadd(self.key_publish, teamid)

    def unpublish(self, teamid):
        self.ch.srem(self.key_publish, teamid)        

    def join_team(self, userid, teamname):
        self.ch.sadd(self.key_ust%userid, teamname)
        self.ch.sadd(self.key_tsm%teamname, userid)

    def remove_team(self, userid, teamname):
        self.ch.srem(self.key_ust%userid, teamname)
        self.ch.srem(self.key_tsm%teamname, userid)

    def is_in_team(self, userid, teamname):
        return self.ch.sismenber(self.key_tsm%teamname,
                                 userid)

    def all_members(self, teamname):
        return self.ch.smembers(self.key_tsm%teamname)

    def user_teams(self, userid):
        return self.ch.smembers(self.key_ust%userid)

    def get_names(self, *teamid):
        return map( lambda x : self.u(self.ch.hget(self.key_name, x)), teamid)

class Permissions(Model):

    u'''
    About the Permissions.

    ch : {set} argo:perm_glb:$permname ==> team set
         {set} argo:perm_brd:$boardname:$permname ==> team set
    '''
    
    key_glb = 'argo:perm_glb:%s'    # Global Permissions
    key_brd = 'argo:perm_brd:%s:%s' # Board's Permissions
    # key_tsp = 'argo:perm_tsp:%s:%s' # Team's Permissions
    key_ust = Team.key_ust

    # Global Permissions

    def give_perm(self, perm, *teamname):
        self.ch.sadd(self.key_glb%perm, *teamname)

    def remove_perm(self, teamname, *perm):
        self.ch.srem(self.key_glb%perm, *teamname)

    def check_perm(self, userid, perm):
        return self.ch.sinter(self.key_ust%userid, self.key_glb%perm)

    def clear_perm(self, perm):
        self.ch.delete(self.key_glb%perm)

    def get_teams_with_perm(self, perm):
        return set(self.u(m) for m in self.ch.smembers(self.key_glb%perm))

    # Board Permissions

    def give_boardperm(self, boardname, perm, *teamname):
        self.ch.sadd(self.key_brd%(boardname, perm), *teamname)

    def remove_boardperm(self, boardname, perm, *teamname):
        self.ch.srem(self.key_brd%(boardname, perm), *teamname)

    def clear_boardperm(self, boardname, perm):
        self.ch.delete(self.key_brd%(boardname, perm))

    def check_boardperm(self, userid, boardname, perm):
        return self.ch.sinter(self.key_ust%userid,
                              self.key_brd%(boardname, perm))

    def checkmany_boardperm(self, userid, boardname, *perms):
        key = self.key_ust%userid
        return map(lambda p : bool(self.ch.sinter(key, self.key_brd%(boardname, p))),
                   perms)

    def check_boardperm_team(self, teamname, boardname, perm):
        return self.ch.sismember(self.key_brd%(boardname, perm), teamname)

    def get_teams_with_boardperm(self, boardname, perm):
        return set( self.u(m) for m in self.ch.smembers(self.key_brd%(boardname, perm)))

class Clipboard(Model):

    u'''
    About the clipboard.

    ch : argo:clipboard:%userid
    '''

    keyf = 'argo:clipboard:%s'
    max_len = 100000
    
    def set_clipboard(self, userid, value=''):
        key = self.keyf % userid
        self.ch.set(key, value)

    def append_clipboard(self, userid, value):
        key = self.keyf % userid
        l = self.ch.strlen(userid)
        if l + len(value) > self.max_len :
            return False
        self.ch.append(key, value)

    def get_clipboard(self, userid):
        key = self.keyf % userid
        return self.u(self.ch.get(key))

class AuthUser(dict):
    def __getattr__(self, name):
        return super(AuthUser,self).get(name)
    def __setattr__(self,name,value):
        self[name] = value

class UserAuth(Model):

    u'''
    An high level module to deal with auth.

    using mod:  userinfo, status, userperm
    '''
    
    ban_userid = ['guest','new']
    GUEST = AuthUser(userid='guest',is_first_login=None)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        
    def gen_passwd(self,passwd):
        return bcrypt.hashpw(passwd, bcrypt.gensalt(10))

    def set_passwd(self, userid, passwd):
        self.table.update_user(userid, passwd=self.gen_passwd(passwd))

    def check_passwd_match(self,passwd,code):
        try:
            return bcrypt.hashpw(passwd, code) == code
        except:
            return False

    def user_exists(self,userid):
        try:
            return bool(self.table.name2id(userid))
        except:
            return False        

    def check_userid(self, userid):
        if len(userid) < 3:
            raise RegistedError(u'此id过短，请至少3个字符以上')
        if userid in self.ban_userid :
            raise RegistedError(u'此id禁止注册')
        if self.user_exists(userid):
            raise RegistedError(u'此帐号已被使用')

    def register(self, userid, passwd, **kwargs):
        self.table.add_user(
            userid=userid,
            passwd=self.gen_passwd(passwd),
            nickname=userid,
            **kwargs
            )
        self.favourite.init_user_favourite(userid)
        self.userperm.init_user_team(userid)
        
    def get_guest(self):
        return self.GUEST

    def login(self, userid, passwd, host, session=True):

        if userid == 'guest':
            raise LoginError(LoginError.NO_SUCH_USER) # Not such user self.get_guest()

        # user_exist
        code = self.table.select_attr(userid,"passwd")
        if code is None :
            raise LoginError(u'没有该用户！')
        code = code['passwd']

        #check_password
        if not self.check_passwd_match(passwd,code):
            raise LoginError(u'帐号和密码不匹配！')
        self.table.update_user(userid,
                               lasthost=host,
                               lastlogin=datetime.now())
        res = self.table.get_user(userid)
        res.is_first_login = res['firstlogin'] == 0

        userid = res['userid']

        if session:
            #set_state
            seid = self.status.new_session(host, userid, 'NEW',
                                           ord(userid[0]))
            if seid is False :
                return LoginError(u'已达最大上线数！')
            res.seid = seid

        if res['userid'] == 'argo' :
            res['is_admin'] = True

        self.msg('Coming :: %s,%s,%s' % (userid,passwd,host))
        self.msg(datetime.now().ctime())

        # print res.seid
        return res

    def msg(self,string):
        print string

    def logout(self, seid):
        self.status.logout(seid)

    def safe_logout(self,seid):
        try:
            self.logout(seid)
        except:
            pass

class Notify(Model):

    _mail = 'argo:notify_mail'
    _notice = 'argo:notify_notice'
    
    def add_mail_notify(self, userid):
        self.ch.hincrby(self._mail, userid)

    def add_notice_notify(self, userid):
        self.ch.hincrby(self._notice, userid)

    def clear_mail_notify(self, userid):
        self.ch.hdel(self._mail, userid)

    def clear_notice_notify(self, userid):
        self.ch.hdel(self._notice, userid)

    def check_mail_notify(self, userid):
        return self.ch.hget(self._mail, userid)

    def check_notice_notify(self, userid):
        return self.ch.hget(self._notice, userid)

class Notice(Model):

    _notice = 'argo:notice:%s'

    max_num = 100

    NOTICE_REPLY = 'r' # r:userid:boardname:pid
    NOTICE_INVE = '@'
    NOTICE_ADDF = 'f'

    def add_notice(self, userid, *args):
        key = self._notice % userid
        self.ch.lpush(key, ':'.join(args))
        self.ch.ltrim(key, 0, self.max_num)

    def get_notice(self, userid, start, limit):
        return map(lambda x : x.split(':'),
                   self.ch.lrange(self._notice % userid,
                                  start, start+limit))

    def add_inve(self, sponer, boardname, pid, userids):
        notice = '@:%s:%s:%s' % (sponer, boardname, pid)
        for u in userids:
            key = self._notice % u
            self.ch.lpush(key, notice)
            self.ch.ltrim(key, 0, self.max_num)

class Action(Model):

    u'''
    High level operation about user's action.
    using mod: board, status, post, mail, userinfo
    '''

    def __init__(self,board,status,post,mail,userinfo,readmark, notify):
        self.board = board
        self.status = status
        self.post = post
        self.mail = mail
        self.userinfo = userinfo
        self.readmark = readmark
        self.notify = notify
        
    def enter_board(self,sessionid,boardname):
        self.status.enter_board(boardname)

    def exit_board(self,sessionid,boardname):
        self.status.exit_board(boardname)

    def new_post(self,boardname,userid,title,content,
                 addr,host,replyable,signature=''):
        bid = self.board.name2id(boardname)
        pid = self.post.add_post(
            boardname,
            bid=bid,
            owner=userid,
            title=title,
            content=content,
            replyid=0,
            fromaddr=addr,
            fromhost=host,
            replyable=replyable,
            signature=signature,
            )
        self.post.update_post(boardname,pid,tid=pid)
        self.board.update_attr_plus1(bid,'total')
        self.board.update_attr_plus1(bid,'topic_total')
        self.readmark.set_read(userid, boardname, pid)
        return pid

    def reply_post(self,boardname,userid,title,content,addr,
                   host,replyid,replyable,signature):
        post = self.post.get_post(boardname, replyid)
        tid = post['tid']
        bid = self.board.name2id(boardname)
        pid = self.post.add_post(
            boardname,
            owner=userid,
            title=title,
            bid=bid,
            content=content,
            replyid=replyid,
            fromaddr=addr,
            fromhost=host,
            tid=tid,
            replyable=replyable,
            signature=signature,
            )
        self.board.update_attr_plus1(bid,'total')
        self.readmark.set_read(userid, boardname, pid)
        # if post['look_reply'] and self.userinfo.user_exist(post['owner']):
        #     self.notice.add_notice(post['owner'],
        #                            Notice.NOTICE_REPLY,
        #                            userid,
        #                            boardname,
        #                            pid)
        #     self.notify.add_notice_notify(post['owner'])
        return pid

    def update_post(self,boardname,userid,pid,content):
        self.post.update_post(boardname,
                              pid,
                              owner = userid,
                              content=content)
    
    def send_mail(self, fromuserid, touserid, **kwargs):
        touid = self.userinfo.name2id(touserid)
        mid =  self.mail.send_mail(touid,
                                   fromuserid=fromuserid,
                                   touserid=touserid,
                                   replyid=0,
                                   **kwargs)
        self.mail.update_mail(touid, mid, tid=mid)
        self.notify.add_mail_notify(touserid)
        return mid

    def reply_mail(self, userid, old_mail, **kwargs):
        touid = self.userinfo.name2id(old_mail['fromuserid'])
        res = self.mail.send_mail(touid,
                                   fromuserid=userid,
                                   touserid=old_mail['fromuserid'],
                                   tid=old_mail['tid'],
                                   replyid=old_mail['mid'],
                                   **kwargs)
        myuid = self.userinfo.name2id(userid)
        self.mail.set_reply(myuid, old_mail['mid'])
        self.notify.add_mail_notify(old_mail['fromuserid'])
        return res

    def del_mail(self,touserid,mid):
        touid = self.userinfo.name2id(touserid)
        return self.mail.del_mail(touid, mid)

    def get_mail(self, userid, num, limit, touid=None):
        touid = touid or self.userinfo.name2id(userid)
        return self.mail.get_mail(touid, userid, num, limit)

    def get_new_mail(self, userid, num, limit):
        touid = self.userinfo.name2id(userid)
        return self.mail.get_new_mail(touid, userid, num, limit)

    def one_mail(self, userid, mid):
        touid = self.userinfo.name2id(userid)
        return self.mail.one_mail(userid, mid)        

    def update_title(self, userid, boardname, pid, new_title):
        return self.post.update_title(boardname, pid, new_title)

    def has_edit_title_perm(self, userid, boardname, pid):
        post = self.post.get_post(boardname, pid)
        return post['owner'] == userid            

class Admin(Model):

    u'''
    High level operation about content admin.
    using mod: board, userperm, post, section
    '''

    def __init__(self, board, userperm, post, section, deny, userinfo, mail):
        self.board = board
        self.userperm = userperm
        self.post = post
        self.section = section
        self.deny = deny
        self.userinfo = userinfo
        self.mail = mail

    def set_post_replyattr(self,userid, boardname, pid, replyable):
        self.post.update_post(boardname, pid, replyable=replyable)

    def add_board(self, userid, boardname, sid, description, allowteam, postteam, denyteam, adminteam):
        self.board.add_board(boardname=boardname, description=description, sid=sid)
        self.userperm.init_boardteam(boardname)
        self.userperm.set_board_allow(boardname, allowteam)
        self.userperm.set_board_post(boardname, postteam)
        self.userperm.set_board_deny(boardname, denyteam)
        self.userperm.set_board_admin(boardname, adminteam)
        self.post._create_table(boardname)
        self.post._create_table_junk(boardname)

    def update_board(self, userid, bid, boardname, sid, description, is_open, is_openw):
        self.board.update_board(bid, boardname=boardname,
                                description=description, sid=sid)
        self.userperm.init_board_team(boardname, is_open, is_openw)

    def join_bm(self, owner, userid, boardname):
        bms = self.board.get_board_bm(boardname)
        if userid in bms:
            raise ValueError(u'%s已经是%s版主'%(userid, boardname))
        bms.append(userid)
        self.board.set_board_bm(boardname, bms)
        self.userperm.join_board_bm(boardname, userid)

    def remove_bm(self, owner, userid, boardname):
        bms = self.board.get_board_bm(boardname)
        if userid not in bms:
            raise ValueError(u'%s不是%s版主'%(userid, boardname))
        bms.remove(userid)
        self.board.set_board_bm(boardname, bms)
        self.userperm.join_board_bm(boardname, userid)

    def set_g_mark(self, userid, board, post):
        if board['perm'][3] :
            post['flag'] = post['flag'] ^ 1
            self.post.update_post(board['boardname'], post['pid'], flag=post['flag'])
        return post

    def set_m_mark(self, userid, board, post):
        if board['perm'][3] :
            post['flag'] = post['flag'] ^ 2
            self.post.update_post(board['boardname'], post['pid'], flag=post['flag'])
        return post

    def remove_post_personal(self, userid, boardname, pid):
        self.post.remove_post_personal(boardname, pid)

    def remove_post_junk(self, userid, boardname, pid):
        self.post.remove_post_junk(boardname, pid)

    def remove_post_junk_range(self, userid, boardname, start, end):
        self.post.remove_post_junk_range(boardname, start, end)

    def send_system_mail(self, touserid, **kwargs):
        touid = self.userinfo.name2id(touserid)
        mid =  self.mail.send_mail(touid,
                                   fromuserid=u'deliver',
                                   touserid=touserid,
                                   replyid=0,
                                   **kwargs)
        self.mail.update_mail(touid, mid, tid=mid)
        return mid

    def deny_user(self, executor, userid, boardname, why, denytime, freetime):
        self.userperm.set_deny(boardname, userid)
        self.deny.deny_user_board(executor, userid, boardname, why, denytime, freetime)
        self.send_system_mail(userid, title=u'%s被 取消在 %s 版的发文权利' % (userid, boardname),
                              content=u"封禁原因 %s , \r\n解封日期 %s " % (why, freetime))

    def undeny_user(self, userid, boardname):
        self.userperm.remove_deny(boardname, userid)
        self.deny.remove_user_deny(userid=userid, boardname=boardname)
        self.send_system_mail(userid, title=u'恢复 %s 在 %s 的发文权利' % (userid, boardname),
                              content=u'你已经被恢复在 %s 版的发文权利' % boardname)

class Deny(Model):

    _d = "argo_denylist"
    _u = "argo_undenylist"

    def get_deny(self, userid, boardname):
        return self.db.get("SELECT * FROM `%s` WHERE userid=%%s AND boardname=%%s" % self._d ,
                           userid, boardname)

    def get_denys(self, boardname, start, limit):
        return self.db.query("SELECT * FROM `%s` "
                             "WHERE boardname=%%s "
                             "ORDER BY id LIMIT %%s,%%s" % self._d,
                             boardname, start, limit)                             

    def deny_user_board(self, executor, userid, boardname, why, denytime, freetime):
        return self.table_insert(self._d, dict(executor=executor, userid=userid,
                                               why=why, boardname=boardname,
                                               denytime=denytime, freetime=freetime))

    def remove_user_deny(self, userid, boardname):
        record = self.get_deny(userid, boardname)
        if not record:
            raise ValueError(u'Not such deny record. [U]{%s} [B]{%s}' % (userid, boardname))
        self.table_insert(self._u, record)
        self.table_delete_by_key(self._d, 'id', record['id'])

class Query:

    u'''
    High level operation about query content.
    using mod: board, userperm, perm, favourite, section, post, userinfo
    '''

    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def _wrap_perm(self, userid, boards):
        rboards = []
        for board in boards:
            board['perm'] = self.userperm.get_board_ability(userid, board['boardname'])
            if board.perm[0] :
                rboards.append(board)
        return rboards

    def get_board_ability(self, userid, boardname):
        return self.userperm.get_board_ability(userid, boardname)

    def get_boards(self, userid, sid=None):
        if sid is None :
            boards = self.board.get_all_boards()
        else:
            boards = self.board.get_by_sid(sid)
        return self._wrap_perm(userid, boards)

    def get_board_by_name(self, userid, boardname):
        board = self.board.get_board(boardname)
        # return self._wrap_perm()    

    def get_all_favourite(self, userid):
        bids = self.favourite.get_all(userid)
        boards = map(lambda d: self.board.get_board_by_id(d), bids)
        return self._wrap_perm(userid, boards)

    def get_section(self, sid):
        return self.section.get_section_by_sid(sid)

    def get_all_section(self):
        return self.section.get_all_section()

    def get_board(self, userid, boardname):
        return self.board.get_board(boardname)

    def get_all_section_with_rownum(self):
        return self.section.get_all_section_with_rownum()

    def get_user(self, userid, toquery):
        base = self.userinfo.get_user(toquery)
        if base :
            base['teams'] = self.team.user_teams(userid)
        return base

    def post_index2pid(self, boardname, index):
        return self.post.index2pid(boardname, index)

class FreqControl(Model):

    u'''
    Limit the user's action frequency.
    Basic usage:

    def action(userid, *args, **kwargs):
        try:
            filter_freq_per(userid)
        except TooFrequentException:
            do_no_thing()
        else:
            do_action(userid, *args, **kwargs)

    Wrap as decorator may be good as well.

    ch : {set} argo:freqcontrol:$userid ==> user set
    
    '''

    keyf = "argo:freqcontrol:%s"

    per = 3
    mid = 15
    big = 120
    
    def _filter_freq(self, userid, fre):
        key = self.keyf % fre
        if self.ch.sismember(key, userid):
            raise TooFrequentException
        if self.ch.exists(key):
            self.ch.sadd(key, userid)
        else:
            self.ch.sadd(key, userid)
            self.ch.expire(key, fre)

    def filter_freq_per(self, userid):
        self._filter_freq(userid, self.per)

    def filter_freq_mid(self, userid):
        self._filter_freq(userid, self.mid)

    def filter_freq_big(self, userid):
        self._filter_freq(userid, self.big)

class Manager:

    u'''
    Mix all model together.
    '''

    @classmethod
    def configure(cls,config):
        cls.db = config.db
        cls.ch = config.ch
        for name in config.use :
            model = config.use[name]
            setattr(cls,name,model)

    def bind(self,**kwargs):
        for k in kwargs:
            setattr(self,k,kwargs[k])

def with_index(d):
    for index in range(len(d)):
        d[index]['rownum'] = index
    return d

def add_column(coldef,after,*tables):
    for table in tables:
        try:
            global_conn.execute("ALTER TABLE `%s` "
                                "ADD COLUMN %s AFTER `%s`" %\
                                    (table, coldef, after))
        except Exception as e:
            print e.message

def update_all(setsql, *tables):
    for table in tables:
        global_conn.execute("UPDATE `%s` "
                            "SET %s" % (table, setsql))

def sql_all_boards(sql):
    d = Board()
    d.bind(global_conn)
    for table in map(lambda x : 'argo_filehead_%s' % x['boardname'],
                     d.get_all_boards()):
        try:
            global_conn.execute(sql % table)
        except Exception as e:
            print '[FAIL] %s' % e.message
        else:
            print '[SUCC] %s' % (sql % table)

def foreach_board(f):
    d = Board()
    d.bind(global_conn)
    for board in d.get_all_boards():
        f(board)

