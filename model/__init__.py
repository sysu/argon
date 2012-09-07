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
    from Model import Section,Status,UserInfo,UserAuth,\
        Board,Post,Action,ReadMark,Mail,Permissions,UserSign,\
        Favourite, Clipboard, Disgest,FreqControl, Team, Admin,\
        Query, Deny, Notify, Notice
    from perm import ArgoTeam
    
    db = global_conn
    ch = global_cache

    section   = Section()
    status    = Status()
    userinfo  = UserInfo()
    usersign  = UserSign()
    board     = Board()
    post      = Post()
    mail      = Mail()
    readmark  = ReadMark(post=post)
    perm      = Permissions()
    favourite = Favourite()
    clipboard = Clipboard()
    disgest   = Disgest()
    freq      = FreqControl()

    notify    = Notify()
    notice    = Notice()
    
    team      = Team()
    userperm  = ArgoTeam(team, perm)
    auth      = UserAuth(table=userinfo,status=status,userperm=userperm, favourite=favourite,
                         team=team)
    action    = Action(board,status,post,mail,userinfo,readmark, notify)
    deny      = Deny()
    admin     = Admin(board, userperm, post, section, deny, userinfo, mail)
    query     = Query(board=board, userperm=userperm, perm=perm, favourite=favourite,
                      section=section, post=post, userinfo=userinfo, team=team)
    
    loads = [section,status,userinfo,auth,board,post,readmark,mail,usersign,
             favourite,clipboard,disgest,freq, perm, team, userperm, admin,
             deny, notify, notice]

    use = {
        "section":section,
        "status":status,
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
        "deny":deny,
        "notify":notify,
        "notice":notice,
        }

    @classmethod
    def load(cls):
        for model in cls.loads :
            model.bind(db = cls.db, ch = cls.ch)

CF.load()
manager = Manager()
Manager.configure(CF)
manager.telnet = {}  # cache use for telnet
