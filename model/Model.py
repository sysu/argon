
#!/usr/bin/python2
# -*- coding: utf-8 -*-

from globaldb import global_conn,global_cache
from MySQLdb import ProgrammingError
import error 
import bcrypt
from datetime import datetime
import mode

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

    __metaclass__ = MetaModel

    def __init__(self):
        self.dict = {}
    
    def bind(self,db=None,ch=None):
        if db : self.db = db
        if ch : self.ch = ch

    def configure(self):
        pass

    def table_select_all(self,tablename):
        return self.db.query("SELECT * FROM %s" % tablename)

    def table_get_by_key(self,tablename,key,value):
        return self.db.get("SELECT * FROM %s WHERE %s = %%s" %\
                               (tablename,key),
                           value)

    def table_insert(self,tablename,attr):
        names,values = zip(*attr.items())
        cols = ','.join(map(str,names))
        vals = ','.join(('%s',) * len(values))
        return self.db.execute("INSERT INTO %s (%s) VALUES (%s)" % \
                                   (tablename, cols,vals),
                               *values)
    
    def table_update_by_key(self,tablename,key,value,attr):
        names,values = zip(*attr.items())
        set_sql = ','.join( map(lambda x: "%s = %%s" % x,names))
        return self.db.execute("UPDATE %s SET %s WHERE %s = %%s" % \
                                   (tablename, set_sql, key),
                               *(values + (value,)))

    def table_delete_by_key(self,tablename,key,value):
        return self.db.execute("DELETE FROM %s WHERE %s = %%s" % \
                                   (tablename, key),
                               value)

    def table_select_by_key(self,tablename,what,key,value):
        return self.db.get("SELECT %s FROM %s WHERE %s = %%s" %\
                               (what, tablename, key),
                           value)

class Section(Model):

    __ = 'argo_sectionhead'

    def get_all_section(self):
        return self.table_select_all(self.__)

    def get_section(self,name):
        return self.table_get_by_key(self.__, 'sectionname', name)

    def add_section(self,**kwargs):
        return self.table_insert(self.__, kwargs)
    
    def update_section(self,sid,**attr):
        return self.table_update_by_key(self.__, 'sid', sid, attr)
    
    def del_section(self,sid):
        return self.table_delete_by_key(self.__, 'sid', sid)
    
    def name2id(self,sectionname):
        d = self.table_select_by_key(self.__, 'sid', 'sectionname', sectionname)
        return d and d['sid']
        
class Board(Model):

    __ = 'argo_boardhead'
    _r = 'argo_recommend'
    
    def get_by_sid(self,sid):
        return self.db.query("SELECT * FROM %s WHERE sid = %%s" % self.__,
                             sid)

    def get_all_boards(self):
        return self.table_select_all(self.__)

    def get_board(self,name):
        return self.table_get_by_key(self.__, 'boardname', name)

    def get_recommend(self):
        return self.db.query(
            "SELECT %s.* FROM %s INNER JOIN %s ON "
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
        d = self.table_select_by_key(self.__, 'bid', 'boardname', boardname)
        return d and d['bid']
    
    def id2name(self,bid):
        d = self.table_select_by_key(self.__, 'boardname', 'bid', bid)
        return d and d['boardname']

    def update_attr_plus1(self,bid,key):
        return self.db.execute("UPDATE %s SET %s = %s +1 WHERE bid = %%s" % \
                                   (self.__, key, key),
                               bid)                               

class Post(Model):

    _prefix = 'argo_filehead_'
    
    def __(self,boardname):
        return self._prefix + boardname

    def _create_table(self,boardname,**kwargs):
        import config
        from string import Template
        with open(config.SQL_TPL_DIR + 'template/argo_filehead.sql') as f :
            board_template = Template(f.read())
            self.db.execute(board_template.safe_substitute(boardname=boardname))

    def get_topic(self,boardname,tid):
        sql = "SELECT * FROM %s WHERE tid = %%s" % self.__(boardname)
        return self.db.query(sql,tid)

    # def _get_posts_advan(self,boardname,order='pid',mark=None,sel='*'):
    #     cond = ''
    #     if mark:
    #         buf = []
    #         'g' in mark and buf.append('flag & 1')
    #         'm' in mark and buf.append('flag & 2')
    #         't' in mark and buf.append('tid = 0')
    #         if buf:
    #             cond = 'WHERE ' + ' AND '.join(buf)
    #     # if offset is None :
    #     #     sql = "SELECT * FROM %s ORDER BY %s %s %s LIMIT %%S" %\
    #     #         (self.__(boardname),order,cond,'DESC' if limit < 0 else '')
    #     #     return self.db.query(sql,abs(limit))
    #     # else:
    #     sql = "SELECT %s FROM %s WHERE %s ORDER BY %s LIMIT %%s,%%s" % \
    #         (sel,self.__(boardname),cond,order)
    #     return sql

    def _query_posts_filter(self,boardname,num,limit,cond=None,order='pid',sel='*'):
        if cond is None:
            cond = []
        if num is not None:
            cond.insert(0,"pid%s%s" % (
                    '>=' if limit > 0 else '<=',
                    num,
                    ))
        if cond :
            cond = 'WHERE %s' % ' AND '.join(cond)
        else : cond = ''
        if limit<0:
            sql = "SELECT %s FROM %s %s ORDER BY %s DESC LIMIT %%s"%\
                (sel,self.__(boardname),cond,order)
            res = self.db.query(sql, -limit)
            res.reverse()
            return res
        else:
            sql = "SELECT %s FROM %s %s ORDER BY %s LIMIT %%s"%\
                (sel,self.__(boardname),cond,order)
            return self.db.query(sql, limit)

    def get_posts(self,boardname,num,limit):
        return self._query_posts_filter(boardname,num,limit)

    def get_posts_g(self,boardname,num,limit):
        return self._query_posts_filter(boardname,num,limit,cond=['flag & 1'])

    def get_posts_g(self,boardname,num,limit):
        return self._query_posts_filter(boardname,num,limit,cond=['flag & 2'])

    def get_posts_topic(self,boardname,num,limit):
        return self._query_posts_filter(boardname,num,limit,cond=['tid=0'])

    def get_last_pid(self,boardname):
        res = self.db.get("SELECT pid FROM %s ORDER BY pid DESC LIMIT 1" % \
                              self.__(boardname))
        return res and res['pid']

    def get_post(self,boardname,pid):
        return self.table_get_by_key(self.__(boardname), 'pid', pid)

    def prev_post_pid(self,boardname,pid):
        res = self.db.get("SELECT pid FROM %s WHERE pid < %s ORDER BY pid DESC LIMIT 1" %\
                              (self.__(boardname),pid))
        return res and res['pid']

    def next_post_pid(self,boardname,pid):
        res = self.db.get("SELECT pid FROM %s WHERE pid > %s ORDER BY pid LIMIT 1" %\
                              (self.__(boardname),pid))
        return res and res['pid']

    def add_post(self,boardname,**kwargs):
        return self.table_insert(self.__(boardname), kwargs)

    def update_post(self,boardname,pid,**kwargs):
        return self.table_update_by_key(self.__(boardname), 'pid', pid, kwargs)

    def del_post(self,*args,**kwargs):
        '''
        Never delete a post.
        '''
        pass

    def get_board_total(self,boardname):
        res = self.db.get("SELECT count(*) as total FROM %s%s" % (self._prefix,boardname))
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
    
class UserInfo(Model):

    __ = 'argo_user'

    def get_user(self,name):
        return self.table_get_by_key(self.__, 'userid', name)

    def add_user(self,**kwargs):
        return self.table_insert(self.__, kwargs)

    def update_user(self,userid,**kwargs):
        return self.table_update_by_key(self.__, 'userid', userid, kwargs)

    def del_user(self,userid):
        '''
        Never delete a user.
        '''
        pass

    def name2id(self,userid):
        '''
        Check if the userid is in database. Return the uid if so,
        or None if not.
        '''
        d = self.table_select_by_key(self.__, 'uid', 'userid', userid)
        return d and d['uid']

    def select_attr(self,userid,sql_what):
        return self.db.get("SELECT %s FROM %s WHERE userid = %%s" % (sql_what, self.__),
                           userid)
class Online(Model):

    def __init__(self,max_login):
        self.max_login = max_login

    def bind(self,db=None,ch=None):
        super(Online,self).bind(db,ch)
        if ch is not None:
            self.ch_status = Cacher('argo:user_statue',ch=self.ch)
            self.ch_sessions = Cacher('argo:user_sessions',ch=self.ch)
            self.ch_board_online = Cacher('argo:board_online',ch=self.ch)
            self.ch_user_ip = Cacher('argo:ip_online',ch=self.ch)

    def login(self,userid):
        d = self.ch_sessions.hget(userid)
        if d and (int(d) >= self.max_login) :
            return False
        self.ch_sessions.hincrby(userid)
        return self.ch_sessions.hget(userid)

    def record_ip(self,userid,sessionid,ip):
        self.ch_user_ip.hmset({userid+sessionid:ip})
            
    def set_state(self,userid,session,value):
        return self.ch_status.hmset({
                userid + session : value
                })

    def get_state(self,userid,session):
        return self.ch_status.hget(userid + session)

    def clear_state(self,userid,session):
        self.ch_status.hdel(userid + session)

    def logout(self,userid,session):
        self.ch_sessions.hincrby(userid,-1)
        print self.ch_sessions.hget(userid)
        if int(self.ch_sessions.hget(userid)) <= 0 :
            self.ch_sessions.hdel(userid)

    def total_online(self):
        return self.ch_sessions.hlen() or 0

    def enter_board(self,boardname,userid,sessionid):
        return self.ch.sadd('argo:board_online:%s'%boardname,
                            userid+':'+sessionid)

    def exit_board(self,boardname,userid,sessionid):
        return self.ch.srem('argo:board_online:%s'%boardname,
                            userid+':'+sessionid)

    def board_online(self,boardname):
        return self.ch.scard('argo:board_online:%s'%boardname)

class AuthUser(dict):
    def __getattr__(self, name):
        return super(AuthUser,self).get(name)
    def __setattr__(self,name,value):
        self[name] = value

class UserAuth(Model):
    
    ban_userid = ['guest','new']

    def __init__(self,usertable,online):
        self.table = usertable
        self.online = online

    def user_exists(self,userid):
        try:
            return bool(self.table.name2id(userid))
        except:
            return False
        
    def is_unvail_userid(self,userid):
        if userid in self.ban_userid :
            return error.REG_BAN_ID
        elif len(userid) < 3 :
            return error.REG_USERID_TOO_SHORT
        elif self.user_exists(userid) :
            return error.REG_REGISTERED
        return error.OK

    def is_unvail_passwd(self,passwd):
        if len(passwd) < 6 :
            return error.REG_PASSWD_TOO_SHORT
        return error.OK

    def gen_passwd(self,passwd):
        return bcrypt.hashpw(passwd, bcrypt.gensalt(10))

    def check_passwd_match(self,passwd,code):
        try:
            return bcrypt.hashpw(passwd, code) == code
        except:
            return False

    def register(self,userid,passwd,**kwargs):
        self.table.add_user(
            userid=userid,
            passwd=self.gen_passwd(passwd),
            nickname=userid,
            **kwargs
            )
        return True

    GUEST = AuthUser(userid='guest',is_first_login=None)
    def get_guest(self):
        return self.GUEST

    def msg(self,string):
        print string

    def login(self,userid,passwd,host,session=True):

        if userid == 'guest':
            return error.LOGIN_NO_SUCH_USER # Not such user self.get_guest()

        # user_exist
        code = self.table.select_attr(userid,"passwd")
        if code is None :
            return error.LOGIN_NO_SUCH_USER # Not such user
        code = code['passwd']

        #check_password
        if not self.check_passwd_match(passwd,code):
            return error.LOGIN_WRONG_PASSWD
        self.table.update_user(userid,
                               lasthost=host,
                               lastlogin=datetime.now())
        res = self.table.get_user(userid)
        res.is_first_login = res['firstlogin'] == 0

        if session:
            #set_state
            seid = self.online.login(userid)
            if seid is False :
                return error.LOGIN_MAX_LOGIN
            res.seid = seid
            self.online.record_ip(userid,seid,host)

        if res['userid'] == 'argo' :
            res['is_admin'] = True

        self.msg('Coming :: %s,%s,%s' % (userid,passwd,host))
        self.msg(datetime.now().ctime())

        # print res.seid
        return res

    def logout(self,userid,seid):
        self.online.logout(userid,seid)

    def safe_logout(self,userid,seid):
        try:
            self.logout(userid,seid)
        except:
            pass

class Mail(Model):

    _prefix = 'argo_mailhead_'

    def __(self,uid):
        return self._prefix + str((int(uid) / 100))

    def _tableid(self,uid):
        return int(uid) / 100

    def _create_table(self,tableid):
        return
        import config
        from string import Template
        with open(config.SQL_TPL_DIR + 'template/argo_mailhead.sql') as f :
            mail_template = Template(f.read())
            self.db.execute(mail_template.safe_substitute(tableid=tableid))
    
    def get_mail_to_uid(self,uid,offset,limit):
        sql = "SELECT * FROM %s WHERE touserid = %%s ORDER BY mid LIMIT %%s,%%s" \
            % self.__(uid)
        try:
            return self.db.query(sql,uid,offset,limit)
        except ProgrammingError,e:
            if e.args[0] == 1146 : # Table NOT EXIST
                self._create_table(self._tableid(uid))
                self.db.query(sql,uid,offset,limit)
            else:
                raise e
    # def get_uid_mail_unread(self,uid,offset,limit):
    #     sql = "SELECT * FROM %S OEDERY BY mid WHERE fromuserid = "\
    #         "%s AND readmark & 1 LIMIT %%s,%%s" % (self.__(uid),uid)
    #     return self.db.query(sql,offset,limit)

    def get_mail(self,uid,mid):
        return self.table_get_by_key(self.__(uid), 'mid', mid)

    def add_mail_touid(self,touid,**kwargs):
        kwargs["touserid"] = touid
        return self.table_insert(self.__(touid),kwargs)

    def del_mail(self,uid,mid):
        return self.table_delete_by_key(self.__(uid),'mid',mid)

class Disgest(Model):

    _prefix = 'argo_annhead_'

    def __(self,partition):
        return self._prefix + partition

    def _create_table(self,partition,**kwargs):
        import config
        from string import Template
        with open(config.SQL_TPL_DIR + 'template/argo_annhead.sql') as f :
            board_template = Template(f.read())
            self.db.execute(board_template.safe_substitute(partition=partition))

    def get_all_books(self,partname):
        sql = "SELECT * FROM %s" % self.__(partname)
        return self.db.query(sql)

    def get_children(self,partname,pid):
        sql = "SELECT * FROM %s WHERE pid = %%s" % self.__(partname)
        return self.db.query(sql,pid)

    def get_node(self,partname,id):
        sql = "SELECT * FROM %s WHERE id = %%s" % self.__(partname)
        return self.db.get(sql,id)
    
class ReadMark(Model):

    keyf = "argo:readmark:%s:%s"

    limit_max = 200
    limit_clear = -50

    def is_read(self,userid,boardname,pid):
        key = self.keyf % (userid, boardname)
        # Empty record, not read
        # And play a trick here, add -1 into read mark
        if self.ch.zcard(key) == 0: 
            self.ch.zaddr(key, -1, -1)
            return 0

        res = self.ch.zcount(key, pid,pid)
        if res: return res
        # If pid is smaller the oldest one in read record, mark as read
        first_pid = self.ch.zrange(self.key%(userid, boardname), 0, 0)[0]
        return pid < int(first_pid)

    def set_read(self,userid,boardname,pid):
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

class Permissions(Model):

    def has_new_post_perm(self,userid,boardname):
        return True

    def has_reply_perm(self,userid,boardname,pid):
        return True

    def has_edit_perm(self,userid,boardname,pid):
        return False

class Action(Model):

    def __init__(self,board,online,post,mail,userinfo):
        self.board = board
        self.online = online
        self.post = post
        self.mail = mail
        self.userinfo = userinfo

    def enter_board(self,userid,sessionid,boardname):
        self.online.enter_board(boardname,userid,sessionid)
        self.online.set_state(userid,sessionid,mode.IN_BOARD)

    def exit_board(self,userid,sessionid,boardname):
        self.online.exit_board(boardname,userid,sessionid)

    def new_post(self,boardname,userid,title,content,addr,host):
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
            )
        self.post.update_post(boardname,pid,tid=pid)
        self.board.update_attr_plus1(bid,'total')
        self.board.update_attr_plus1(bid,'topic_total')

    def reply_post(self,boardname,userid,title,content,addr,host,replyid):
        tid = self.post.pid2tid(boardname,replyid)
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
            )
        self.board.update_attr_plus1(bid,'total')

    def update_post(self,boardname,userid,pid,title,content):
        self.post.update_post(boardname,
                              pid,
                              owner = userid,
                              title=title,
                              content=content)

    def get_rebox_mail(self,userid,offset,limit=20):
        uid = self.userinfo.name2id(userid)
        return self.mail.get_mail_to_uid(uid,offset,limit)

    def send_mail(self,fromuserid,touserid,**kwargs):
        fromuid = self.userinfo.name2id(fromuserid)
        touid = self.userinfo.name2id(touserid)
        self.mail.add_mail_touid(touid,fromuserid=fromuid,**kwargs)

    def del_mail(self,touserid,mid):
        touid = self.userinfo.name2id(touserid)
        self.mail.del_mail(touid,mid)

    def get_mail(self,userid,mid):
        uid = self.userinfo.name2id(userid)
        return self.mail.get_mail(uid,mid)

    def update_title(self,userid,boardname,pid,new_title):
        return self.post.update_title(boardname,pid,new_title)
                   
class Manager:

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
