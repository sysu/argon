import MySQLdb
import cPickle
import config

# from Model import *
# from Model import db_orm

from board import Board
from user import User
from post import Post
from section import Section

def init_database():
    from globaldb import global_conn as db
    for table_name in config.BASE_TABLE :
        with open(config.SQL_TPL_DIR+'argo_'+table_name+'.sql') as f:
            sql = f.read()
            print sql
            db.execute(sql)
