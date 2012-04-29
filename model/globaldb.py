#!/usr/bin/env python

import  dbapi
from config import  dbConfig

dbcfg = dbConfig()

global_conn = dbapi.Connection(host=dbcfg.host+':'+str(dbcfg.port), user=dbcfg.user, password=dbcfg.passwd, database=dbcfg.dbname)

print 'init global_conn'

