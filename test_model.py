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

    def test_all(self):
        from random import randint
        rand = 007
        sname = "Section"
        bname = "Board"
        work = (
            ("get_all_section",tuple()),
            # ("add_section",(sname,"Test section [%s]" % rand)),
            # ("add_board",(bname,sname,"DESC")),
            ("get_all_board",tuple()),
            ("add_post",(bname,"Title","OWNER","CONTENT","from")),
            ("get_board_post",(bname, 0 ,200)),
            )
        for method,args in work :
            print "------------------------ Start test {{%s}} " % method
            getattr(self,method)(*args)
            print "------------------------ DONE"
    
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
        secs = model.Section.get_all()
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

    def add_board(self,boardname,sectionname,description):
        u'''
        增加一个讨论区。
        '''
        sid = model.Section.get_sid_by_name(sectionname)
        if sid is None:
            print 'No such section [%s] ' % sectionname
        else:
            b = model.Board(boardname=boardname,
                            sid=sid,
                            description=description)
            b.save()
            print 'Add board %s to %s DONE. ' % (boardname,sectionname)

    def get_section_board(self,sectionname):
        sid = model.Section.get_sid_by_name(sectionname)
        res = model.Board.get_board_by_sid(sid = sid)
        print '\r\n'.join(map(str,res))

    def get_all_board(self):
        res = model.Board.get_all()
        print '\n'.join(map(str,res))

    def add_post(self,boardname,title,owner,content,fromhost):
        p = model.Post(bid = model.Board.get_bid_by_name(boardname),
                 title = title,owner=owner,content=content,fromhost=fromhost)
        p.save()
        print "Add post %s to %s DONE." % (title,boardname)

    def get_board_post(self, boardname, offset, limit):
        res = model.Post.get_by_bid(
            model.Board.get_bid_by_name(boardname),int(offset),int(limit))
        print '\r\n'.join(map(str,res))

    def add_user(self,userid,passwd):
        model.User.add_user(userid=userid,passwd=passwd)
                                    
    def get_user(self, userid):
        uid = model.User.get_uid_by_userid(userid)
        d = model.User.get(uid)
        print str(d)

    def get_user_auth(self, userid, passwd):
        print model.User.get_user_auth(userid,passwd)

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
