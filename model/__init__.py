import status
import argo_conf
from error import *

def init_database():
    for table_name in argo_conf.BASE_TABLE :
        init_table(table_name)

def init_table(table_name):
    from globaldb import global_conn as db
    with open(argo_conf.SQL_DIR+'argo_'+table_name+'.sql') as f:
        sql = f.read()
        print sql
        try:
            db.execute(sql)
        except Exception as e:
            print e
            raw_input('>> ')

MODULE_NAME = {
    "Permissions" : "perm",
    "FreqControl" : "freq",
    "ArgoTeam" : "userperm",
    "UserAuth" : "auth",
    "WebConfigure" : "web",
    }

def get_telnet_manager():
    from globaldb import global_conn, global_cache
    from Model import Section, Status, UserInfo, UserSign, Board,\
        Post, Mail, ReadMark, Permissions, Favourite, Clipboard,\
        Disgest, FreqControl, Notify, Notice, Team, \
        UserAuth, Deny, Admin, Query, Manager, Action, WebConfigure
    from perm import ArgoTeam
    return Manager(global_conn, global_cache, [
            Section, Status, UserInfo, UserSign, Board, Post, Mail,
            ReadMark, Permissions, Favourite, Clipboard, Disgest,
            FreqControl, Notify, Notice, Team, ArgoTeam, UserAuth,
            Deny, Admin, Query, Action, WebConfigure,
            ], MODULE_NAME)

manager = get_telnet_manager()
manager.telnet = {}

