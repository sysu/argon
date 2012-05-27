import MySQLdb
import cPickle
import config

from Model import Manager

def init_database():
    from globaldb import global_conn as db
    for table_name in config.BASE_TABLE :
        with open(config.SQL_TPL_DIR+'argo_'+table_name+'.sql') as f:
            sql = f.read()
            print sql
            db.execute(sql)

class CF:

    from globaldb import global_conn,global_cache
    from Model import Section,Online,UserInfo,UserAuth
    
    db = global_conn
    ch = global_cache

    section   = Section()
    online    = Online(max_login=3)
    userinfo  = UserInfo()
    auth      = UserAuth(userinfo,online)

    loads = [section,online,userinfo,auth]

    use = {
        "section":section,
        "online":online,
        "auth":auth,
        }

manager = Manager(CF)
