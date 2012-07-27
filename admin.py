#!/usr/bin/env python
# -*- coding: utf-8 -*-

import model
import sys,inspect
import argo_conf as cc
from argo_conf import ConfigTestDate as t

manager = model.manager

def init_database():
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

def r():
    reload(model)
    global manager
    manager = model.manager

def bpp(ll):
    print '\n'.join(map(str, ll))

print u'''\

Enjoy it . :-)

loading model ...
loading manager ...
loading init_database ...

'''
