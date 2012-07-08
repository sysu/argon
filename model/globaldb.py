# -*- coding: utf-8 -*-
#!/usr/bin/env python

import  dbapi
from config import *
import redis

class GlobalDB(object):
    
    conn = dbapi.Connection(host=HOST+':'+str(PORT), user=USER, password=PASSWD, database=DBNAME)
    cache = redis.Redis(host=CHOST, port=CPORT)


global_conn = GlobalDB.conn
global_cache = GlobalDB.cache


