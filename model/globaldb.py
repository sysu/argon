# -*- coding: utf-8 -*-
#!/usr/bin/env python

import  dbapi
from config import *
import redis

def connect_db():
    return dbapi.Connection(host=HOST+':'+str(PORT), user=USER, password=PASSWD, database=DBNAME)

def connect_ch():
    return redis.Redis(host=CHOST, port=CPORT)

class GlobalDB(object):

    conn = connect_db()
    cache = connect_ch()

global_conn = GlobalDB.conn
global_cache = GlobalDB.cache
