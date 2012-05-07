# -*- coding: utf-8 -*-
#!/usr/bin/env python

from model.Model import db_orm,Post
from datetime import datetime

import sys,inspect

"""
    Uint test for db_orm
"""

class TestSuit(object):

    def init_database(self):
        u'''
        初始化数据库。
        '''
        print
        print 'Init Database will kill all data. Are you sure?'
        print
        print 'Type INIT_YES to continue.',
        if raw_input() == 'INIT_YES' :
            print 'Init Database start ...'
            db_orm.init_database()
            print 'Init Database DONE.'
        print 'All DONE.'

    def get_all_section(self):
        u'''
        输出全部的讨论区。
        '''
        print '\r\n'.join(map(str,db_orm.get_all_section()))

    def add_section(self,sectionname,description):
        u'''
        增加一个讨论区。
        '''
        print 'Add Section : [%s] %s' % (sectionname,description)
        db_orm.add_section(sectionname,{"description":description})
        print 'All DONE.'

    def del_section(self,sectionname):
        u'''
        删除一个讨论区。
        '''
        print 'Del Section : [%s] ' % sectionname
        db_orm.del_section(sectionname)
        print 'All DONE.'

    def get_section(self, sname = 'Test'):
        s = db_orm.get_section(sname)
        print s
        print s.dump_attr()
        print s.get_allboards()

    def add_board(self,boardname,section,description):
        u'''
        增加一个讨论区。
        '''
        db_orm.add_board(
            boardname.decode('utf8'),section.decode('utf8'),
            {"description":description.decode('utf8')})
        print 'Add board %s to %s DONE. ' % (boardname,section)

    def get_section_board(self,section_name):
        b = db_orm.get_section(section_name.decode('utf8'))
        for board in b.get_allboards() :
            print board.dump_attr()

    def add_post(self,boardname,title,owner,content,fromhost):
        b = db_orm.get_board(boardname)
        b.add_post(Post({
                    "title":title.decode('utf8'),
                    "owner":owner.decode('utf8'),
                    "content":content.decode('utf8'),
                    "fromhost":fromhost.decode('utf8'),
                    }))
        print "Add post %s to %s DONE." % (title,boardname)

    def add_user(self,userid,passwd):
        db_orm.add_user(userid,passwd,{'firstlogin':datetime.now()})
        print 'Add user %s DONE.' % userid

    def get_user(self, userid = 'Jia'):
        u = db_orm.get_user(userid)
        print u.dump_attr()

    def login(self, name, passwd):
        u = db_orm.login(name, passwd)
        if u == None:
            print 'login error'
            return

        print 'online: ' , db_orm.get_online_users()
        print u.dump_attr()

    def online_users(self):
        users = db_orm.get_online_users()
        print users

    def help(self,command):
        foo = getattr(self,command)
        print
        print command + ' [' + ' '.join(inspect.getargspec(foo)[0][1:]) +']\n'
        print getattr(self,command).__doc__

    def usage(self):
        print '\r\n'.join(filter(lambda x : not x.endswith('__'),dir(self)))

    def run(self):
        while True:
            input()

t = TestSuit()
if len(sys.argv) < 2: t.usage()
else:
    getattr(t, sys.argv[1])(*sys.argv[2:])


