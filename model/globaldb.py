# -*- coding: utf-8 -*-
#!/usr/bin/env python

from __future__ import absolute_import, division, with_statement

import copy
import itertools
import logging
import time
import redis

try:
    import MySQLdb.constants
    import MySQLdb.converters
    import MySQLdb.cursors
    import MySQLdb
except ImportError:
    # If MySQLdb isn't available this module won't actually be useable,
    # but we want it to at least be importable (mainly for readthedocs.org,
    # which has limitations on third-party modules)
    MySQLdb = None

logger = logging.getLogger('globaldb')

class BaseDBConnection:

    def query(self, query, *parameters):
        """Returns a row list for the given query and parameters."""
        logger.debug('QUERY{{%s}}[[%s]]', query, parameters)
        conn = self._conn()
        cursor = conn.cursor()
        try:
            self._execute(cursor, query, parameters)
            column_names = [d[0] for d in cursor.description]
            return [Row(itertools.izip(column_names, row)) for row in cursor]
        finally:
            cursor.close()
            self._finish_conn(conn)
    
    def get(self, query, *parameters):
        """Returns the first row returned for the given query."""
        rows = self.query(query, *parameters)
        if not rows:
            return None
        elif len(rows) > 1:
            raise Exception("Multiple rows returned for Database.get() query")
        else:
            return rows[0]

    def escape_string(self, rowsql):
        return MySQLdb.escape_string(rowsql)

    # rowcount is a more reasonable default return value than lastrowid,
    # but for historical compatibility execute() must return lastrowid.
    def execute(self, query, *parameters):
        """Executes the given query, returning the lastrowid from the query."""
        return self.execute_lastrowid(query, *parameters)

    def execute_lastrowid(self, query, *parameters):
        """Executes the given query, returning the lastrowid from the query."""
        logger.debug('EXECUTE{{%s}}[[%s]]', query, parameters)
        conn = self._conn()
        cursor = conn.cursor()
        try:
            self._execute(cursor, query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()
            self._finish_conn(conn)

    def _execute(self, cursor, query, parameters):
        # try:
            return cursor.execute(query, parameters)
        # except OperationalError:
        #     logging.error("Error connecting to MySQL")
        #     self.close()
        #     raise

    def execute_rowcount(self, query, *parameters):
        """Executes the given query, returning the rowcount from the query."""
        conn = self._conn()
        cursor = conn.cursor()
        try:
            self._execute(cursor, query, parameters)
            return cursor.rowcount
        finally:
            cursor.close()
            self._finish_conn(conn)

    def executemany(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        return self.executemany_lastrowid(query, parameters)

    def executemany_lastrowid(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        conn = self._conn()
        cursor = conn.cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()
            self._finish_conn(conn)

    def executemany_rowcount(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the rowcount from the query.
        """
        conn = self._conn()
        cursor = conn.cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.rowcount
        finally:
            cursor.close()
            self._finish_conn(conn)
            
    def execute_paragraph(self, para):
        conn = self._conn()
        cursor = conn.cursor()
        try:
            try:
                cursor.execute(para)
            except MySQLdb.ProgrammingError as e:
                if e.args[0] == 2014:
                    print e.message
                    pass
                else:
                    raise e
            more = True
            while more:
                cursor.fetchall()
                more = cursor.nextset()
            return cursor.rowcount
        finally:
            cursor.close()
            self._close_conn(conn)

    def _conn(self):
        raise NotImplementedError

    def _close_conn(self):
        raise NotImplementedError

class Row(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

class NormalDBConnection(BaseDBConnection):

    def __init__(self, host, database, user=None, password=None,
                 max_idle_time=7 * 3600):
        self.host = host
        self.database = database
        self.max_idle_time = max_idle_time

        args = dict(conv=CONVERSIONS, use_unicode=True, charset="utf8",
                    db=database, init_command='SET time_zone = "+0:00"',
                    sql_mode="TRADITIONAL")
        if user is not None:
            args["user"] = user
        if password is not None:
            args["passwd"] = password

        # We accept a path to a MySQL socket file or a host(:port) string
        if "/" in host:
            args["unix_socket"] = host
        else:
            self.socket = None
            pair = host.split(":")
            if len(pair) == 2:
                args["host"] = pair[0]
                args["port"] = int(pair[1])
            else:
                args["host"] = host
                args["port"] = 3306

        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except Exception:
            logging.error("Cannot connect to MySQL on %s", self.host,
                          exc_info=True)

    def __del__(self):
        self.close()

    def close(self):
        """Closes this database connection."""
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._db = MySQLdb.connect(**self._db_args)
        self._db.autocommit(True)

    def _ensure_connected(self):
        # Mysql by default closes client connections that are idle for
        # 8 hours, but the client library does not report this fact until
        # you try to perform a query and it fails.  Protect against this
        # case by preemptively closing and reopening the connection
        # if it has been idle for too long (7 hours by default).
        if (self._db is None or
            (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()

    def _conn(self):
        self._ensure_connected()
        return self._db

    def _finish_conn(self, conn):
        self._last_use_time = time.time()

class EventLetDBPool(BaseDBConnection):

    def __init__(self, host, database, user=None, password=None):
        args = dict(conv=CONVERSIONS, use_unicode=True, charset="utf8",
                    db=database,
                    init_command='SET time_zone = "+0:00"',
                    sql_mode="TRADITIONAL")
        if user is not None:
            args['user'] = user
        if password is not None:
            args['passwd'] = password
        if '/' in host:
            args['unix_socket'] = host
        else:
            self.socket = None
            pair = host.split(":")
            if len(pair) == 2:
                args["host"] = pair[0]
                args["port"] = int(pair[1])
            else:
                args["host"] = host
                args["port"] = 3306
        from eventlet import db_pool
        self._pool = db_pool.ConnectionPool(MySQLdb, **args)

    def _conn(self):
        conn = self._pool.get()
        conn.autocommit(True)
        return conn

    def _finish_conn(self, conn):
        self._pool.put(conn)

if MySQLdb is not None:
    # Fix the access conversions to properly recognize unicode/binary
    FIELD_TYPE = MySQLdb.constants.FIELD_TYPE
    FLAG = MySQLdb.constants.FLAG
    CONVERSIONS = copy.copy(MySQLdb.converters.conversions)

    field_types = [FIELD_TYPE.BLOB, FIELD_TYPE.STRING, FIELD_TYPE.VAR_STRING]
    if 'VARCHAR' in vars(FIELD_TYPE):
        field_types.append(FIELD_TYPE.VARCHAR)

    for field_type in field_types:
        CONVERSIONS[field_type] = [(FLAG.BINARY, str)] + CONVERSIONS[field_type]

    # Alias some common MySQL exceptions
    IntegrityError = MySQLdb.IntegrityError
    OperationalError = MySQLdb.OperationalError

def connect_db():
    from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWD, DB_NAME
    try:
        from config import USE_EVENTLET_DB_POOL
    except ImportError:
        USE_EVENTLET_DB_POOL = False
    if USE_EVENTLET_DB_POOL :
        logger.info('use eventlet db pool')
        return EventLetDBPool(host='%s:%s' % (DB_HOST, DB_PORT),
                              user=DB_USER, password=DB_PASSWD,
                              database=DB_NAME)
    else:
        logger.info('use normal db connection')
        return NormalDBConnection(host='%s:%s' % (DB_HOST,
                                                  DB_PORT),
                                  user=DB_USER,
                                  password=DB_PASSWD,
                                  database=DB_NAME)
    
def connect_ch():
    from config import REDIS_HOST, REDIS_PORT
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

global_conn = connect_db()
global_cache = connect_ch()

