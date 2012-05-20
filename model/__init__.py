import MySQLdb
import cPickle
import config
# from Model import *
# from Model import db_orm

from board import Board
from user import User
from post import Post
from section import Section

all_tables = [Board,User,Post,Section]

def init_database():
    for t in all_tables :
        t.init()
