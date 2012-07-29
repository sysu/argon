import MySQLdb
import cPickle
import config

from Model import Manager
from error import *

def init_database():
    for table_name in config.BASE_TABLE :
        init_table(table_name)

def init_table(table_name):
    from globaldb import global_conn as db
    with open(config.SQL_TPL_DIR+'argo_'+table_name+'.sql') as f:
        sql = f.read()
        print sql
        try:
            db.execute(sql)
        except Exception as e:
            print e
            raw_input('>> ')

class CF:

    from globaldb import global_conn,global_cache
    from Model import Section,Online,UserInfo,UserAuth,\
        Board,Post,Action,ReadMark,Mail,Permissions,UserSign,\
        Favourite, Clipboard, Disgest,FreqControl, Team, UserPerm,\
        Admin, Query
    
    db = global_conn
    ch = global_cache

    section   = Section()
    online    = Online(max_login=9999)
    userinfo  = UserInfo()
    usersign  = UserSign()
    board     = Board()
    post      = Post()
    mail      = Mail()
    action    = Action(board,online,post,mail,userinfo)
    perm      = Permissions()
    readmark  = ReadMark(post=post)
    favourite = Favourite()
    clipboard = Clipboard()
    disgest   = Disgest()
    freq      = FreqControl()
    team      = Team()
    userperm  = UserPerm(team, perm)
    auth      = UserAuth(userinfo,online,userperm)
    admin     = Admin(board, userperm, post, section)
    query     = Query(board=board, userperm=userperm, perm=perm, favourite=favourite,
                      section=section, post=post, userinfo=userinfo)
    
    loads = [section,online,userinfo,auth,board,post,readmark,mail,usersign,
             favourite,clipboard,disgest,freq, perm, team, userperm, admin]

    use = {
        "section":section,
        "online":online,
        "userinfo":userinfo,
        "auth":auth,
        "board":board,
        "post":post,
        "action":action,
        "readmark":readmark,
        "perm":perm,
        "usersign":usersign,
        "favourite":favourite,
        "mail":mail,
        "clipboard":clipboard,
        "disgest":disgest,
        "freq":freq,
        "userperm":userperm,
        "team":team,
        "admin":admin,
        "query":query,
        }

    @classmethod
    def load(cls):
        for model in cls.loads :
            model.bind(db = cls.db, ch = cls.ch)

CF.load()
manager = Manager()
Manager.configure(CF)
