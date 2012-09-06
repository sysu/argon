# -*- coding: utf-8 -*-
#!/usr/bin/env python

import  dbapi
from config import *
from eventlet import db_pool
import MySQLdb
import redis
import logging

logger = logging.getLogger('globaldb')

class DBConnectionPool:

    _db_pool = None

    def __init__(self, host, user, password, database):
        self._db_pool = db_pool.ConnectionPool(dbapi, host=host, user=user, password=password, database=database)

    def query(self, query, *parameters):
        logger.debug('SQL:%s $%s', query, parameters)
        conn = self._db_pool.get();
        try:
            return conn.cursor().query(query, *parameters)
        finally:
            self._db_pool.put(conn)

    def get(self, query, *parameters):
        logger.debug('SQL:%s $%s', query, parameters)
        conn = self._db_pool.get()
        try:
            return conn.cursor().get(query, *parameters)
        finally:
            self._db_pool.put(conn)

    def escape_string(self, rowsql):
        conn = self._db_pool.get()
        try:
            return conn.cursor().escape_string(rowsql)
        finally:
            self._db_pool.put(conn)

    def execute(self, query, *parameters):
        logger.debug('SQL:%s $%s', query, parameters)
        conn = self._db_pool.get()
        try:
            return conn.cursor().execute(query, *parameters)
        finally:
            self._db_pool.put(conn)

    def executemany(self, query, parameters):
        logger.debug('SQL:%s $%s', query, parameters)
        conn = self._db_pool.get()
        try:
            return conn.cursor().executemany(query, parameters)
        finally:
            self._db_pool.put(conn)

    ############  Add to support execute from files  ###########################
    def execute_paragraph(self, para):
        logger.debug('SQL:%s $%s', query, parameters)
        conn = self._db_pool.get()
        try:
            return conn.cursor().execute_paragraph(para)
        finally:
            self._db_pool.put(conn)

def connect_db():

    return DBConnectionPool(host=HOST+':'+str(PORT), user=USER, password=PASSWD, database=DBNAME)
    #return dbapi.Connection(host=HOST+':'+str(PORT), user=USER, password=PASSWD, database=DBNAME)

def connect_ch():
    return redis.Redis(host=CHOST, port=CPORT)

class GlobalDB(object):

    conn = connect_db()
    cache = connect_ch()

global_conn = GlobalDB.conn
global_cache = GlobalDB.cache

