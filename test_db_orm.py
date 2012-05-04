# -*- coding: utf-8 -*-
#!/usr/bin/env python

from model.Model import db_orm

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

    def get_section(self):
        s = db_orm.get_section('Test')
        print s
        print s.dump_attr()
        print s.get_allboards()

    def add_board(self):
        db_orm.add_board('TestTwo','Test',{"description":"Board for test two."})

    def get_board(self):
        b = db_orm.get_board('Test')
        print b.dump_attr()

    def add_user(self):
        u = db_orm.add_user('Jia','2022',{"email":"no@e.com"})

    def get_user(self):
        u = db_orm.get_user('Jia')
        print u.dump_attr()

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

