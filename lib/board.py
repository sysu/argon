# -*- coding: utf-8 -*-

import sys
sys.path.append('../model/')

'''
    建议sql语句都放在model下，lib最多通过db_orm实现数据操作
'''
from globaldb import global_conn as db
from hashlib import md5

def insert_dict(table,kv_pairs):
    exist_attr = kv_pairs.keys()
    exist_val = map(lambda x : "'%s'" % x,kv_pairs.values())
    sql = "INSERT INTO %s(%s) values(%s)" % (table, ','.join(exist_attr), ','.join(exist_val))
    db.execute(sql)

with open('../database/template/argo_filehead.sql') as f :
    new_board_text = f.read()

def set_up_new_board(boardname,keys):
    keys['boardname'] = boardname
    db.execute(new_board_text % { "boardname":boardname})
    insert_dict('argo_boardhead',keys)

def register(username,passwd,keys):
    keys['userid'] = username
    m = md5()
    m.update(passwd)
    keys['passwd'] = m.hexdigest()
    insert_dict('argo_user',keys)

def check_login(username,passwd):
    m = md5()
    m.update(passwd)
    passwd = m.hexdigest()
    sql = "SELECT * FROM argo_user WHERE userid = '%s' and passwd = '%s' " % ( username, passwd)
    print sql
    res = db.query(sql)
    print repr(res)

def get_boardlist_q(sid):
    return [
        {
            "boardname":u"Selection",
            "flag":False,
            "bid":0,
            "total":635,
            "descript":u"选举事务",
            "bm":u"jmf",
            "type":u"本站",
            "online":5,
            },
        ] * 50

def get_board_info(bid):
    '''
    返回bid为bid的讨论区的信息。
    '''
    return {
        "sid":0,
        "boardname":"z",
        }
