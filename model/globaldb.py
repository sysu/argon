# -*- coding: utf-8 -*-
#!/usr/bin/env python

import  dbapi
from config import *
import redis

global_conn = dbapi.Connection(host=HOST+':'+str(PORT), user=USER, password=PASSWD, database=DBNAME)

'''
    采用redis做cache及全局通信,替代原来的shm功能
'''
global_cache = redis.Redis(host=CHOST, port=CPORT)


