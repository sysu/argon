#!/usr/bin/env python
# -*- coding: utf-8 -*-

__metaclass__ = type

import model
from datetime import datetime

import sys,inspect

"""
    Uint test for db_orm
"""

class Holder:

    ### TODO
    
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
            model.init_database()
            print 'Init Database DONE.'
        print 'All DONE.'

    def get_all_section(self):
        u'''
        输出全部的讨论区。
        '''
        secs = model.Section.all()
        print '\r\n'.join(map(str,secs))

    def add_section(self,sectionname,description):
        u'''
        增加一个讨论区。
        '''
        print 'Add Section : [%s] %s' % (sectionname,description)
        s = model.Section(sectionname=sectionname,description=description)
        s.save()
        print 'All DONE.'

    def del_section(self,sectionname):
        u'''
        删除一个讨论区。
        '''
        print 'Del Section : [%s] ' % sectionname
        s = model.Section.get_by_sectionname(sectionname)
        if s is None :
            print 'No such Section.'
        else:
            s.delete()
            print 'All DONE.'

    # def add_board(self,boardname,sectionname,description):
    #     u'''
    #     增加一个讨论区。
    #     '''
    #     b = model.Board(boardname=boardname,
    #                     sid=model.Section.get_sid_by_name(sectionname),
    #                     description=description)
    #     b.save()
    #     print 'Add board %s to %s DONE. ' % (boardname,sectionname)

    # def get_section_board(self,sectionname):
    #     res = model.Board.all(sid = model.Section.get_sid_by_name(sectionname))
    #     print '\r\n'.join(map(str,res))

    # def add_post(self,boardname,title,owner,content,fromhost):
    #     p = model.Post(bid = model.Board.get_id_by_name(boardname),
    #              title = title,owner=owner,content=content,fromhost=fromhost)
    #     p.save()
    #     print "Add post %s to %s DONE." % (title,boardname)

    # def get_board_post(self,boardname):
    #     b = db_orm.get_board(boardname)
    #     da = b.get_post(0)
    #     for post in da :
    #         print post.dict
            
    # def add_user(self,userid,passwd):
    #     db_orm.add_user(userid,passwd,{'firstlogin':datetime.now()})
    #     print 'Add user %s DONE.' % userid

    # def get_user(self, userid = 'Jia'):
    #     u = db_orm.get_user(userid)
    #     print u.dump_attr()

    # def login(self, name, passwd):
    #     u = db_orm.login(name, passwd)
    #     if u == None:
    #         print 'login error'
    #         return

    #     print 'online: ' , db_orm.get_online_users()
    #     print u.dump_attr()

    # def online_users(self):
    #     users = db_orm.get_online_users()
    #     print users

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

t = Holder()
if len(sys.argv) < 2: t.usage()
else:
    getattr(t, sys.argv[1])(*sys.argv[2:])
