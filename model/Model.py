#!/usr/bin/python2
# -*- coding: utf-8 -*-

from globaldb import global_conn,global_cache
import error 
import bcrypt
from datetime import datetime

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
        pass
    
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
    
    def del_section(self,sectionname):
        return self.table_delete_by_key(self.__, 'sectionname', sectionname)
    
    def name2id(self,sectionname):
        d = self.table_select_by_key(self.__, 'sid', 'sectionname', sectionname)
        return d and d['sid']
        
class Board(Model):

    __ = 'argo_boardhead'

    def get_by_sid(self,sid):
        return self.db.query("SELECT * FROM %s WHERE sid = %%s" % self.__,
                             sid)

    def get_all_board(self):
        return self.table_select_all(self.__)

    def get_board(self,name):
        return self.table_get_by_key(self.__, 'boardname')

    def add_board(self,**kwargs):
        return self.table_insert(self.__, kwargs)
    
    def update_board(self,bid,**attr):
        return self.table_update_by_key(self.__, 'bid', bid, attr)
    
    def del_board(self,boardname):
        return self.table_delete_by_key(self.__, 'boardname', boardname)
    
    def name2id(self,boardname):
        d = self.table_select_by_key(self.__, 'bid', 'boardname', boardname)
        return d and d['bid']

class Post(Model):

    _prefix = 'argo_filehead_'
    
    @property
    def __(self,boardname):
        return self._prefix + boardname

    def get_posts_by_boardname(self,boardname,offset,limit):
        return self.db.query("SELECT * FROM %s ORDER BY pid LIMIT %%s,%%s" % \
                                 self.__(boardname),
                             offset,limit)

    def get_topic_by_boardname(self,boardname,offset,limit):
        return self.db.query("SELECT * FROM %s WHERE tid = 0 ORDER BY pid LIMIT %%s,%%s" % \
                                 self.__(boardname),
                             offset,limit)

    def get_post(self,boardname,pid):
        return self.table_get_by_key(self.__(boardname), 'pid', pid)

    def add_post(self,boardname,**kwargs):
        return self.table_insert(self.__(boardname), kwargs)

    def update_post(self,boardname,**kwargs):
        return self.table_update_by_key(self.__(boardname), 'pid', pid, attr)

    def del_post(self,*args,**kwargs):
        '''
        Never delete a post.
        '''
        pass

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
class Mail(Model):
    pass

class Online(Model):

    def __init__(self,max_login):
        self.max_login = max_login

    def bind(self,db=None,ch=None):
        super(Online,self).bind(db,ch)
        if ch is not None:
            self.ch_status = Cacher('argo:user_statue',ch=self.ch)
            self.ch_sessions = Cacher('argo:user_sessions',ch=self.ch)
            self.ch_board_online = Cacher('argo:board_online',ch=self.ch)

    def login(self,userid):
        d = self.ch_sessions.hget(userid)
        if d and (int(d) >= self.max_login) :
            return False
        self.ch_sessions.hincrby(userid)
        return self.ch_sessions.hget(userid)
            
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
        if int(self.ch_sessions.hget(userid)) <= 0 :
            self.ch_sessions.hdel(userid)

    def total_online(self):
        return self.ch_sessions.hlen() or 0

    def enter_board(self,boardname):
        return self.ch_board_online.hincrby(boardname)

    def exit_board(self,boardname):
        return self.ch_board_online.hincrby(boardname,-1)

    def board_online(self,boardname):
        return self.ch_board_online.hget(boardname)

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

    def login(self,userid,passwd,host):

        if userid == 'guest':
            return self.get_guest()

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

        #set_state
        seid = self.online.login(userid)
        # if seid is False :
        #     return error.LOGIN_MAX_LOGIN
        res.seid = seid

        if res['userid'] == 'argo' :
            res['is_admin'] = True
        
        return res

    def logout(self,userid):
        pass
        #set_state
        # self.online.
        
class ReadMark(Model):
    pass

class Manager:

    def __init__(self,config):
        
        self.db = config.db
        self.ch = config.ch
        
        for model in config.loads :
            model.bind(db = config.db,
                       ch = config.ch)
            
        for name in config.use :
            model = config.use[name]
            setattr(self,name,model)
