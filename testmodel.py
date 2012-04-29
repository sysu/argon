#!/usr/bin/env python

from model import Model

"""
    Unit test for Model.
"""


m = Model.Model()

m.connect()
m.query("show tables")
print m.fetchall()

m.closedb()

"""
It may generate information like this:

Connect bbs@172.18.42.164:3306 pwd=forargo db=argo
(('argo_attachead',), ('argo_boardhead',), ('argo_filehead_Test',), ('argo_sectionhead',), ('argo_user',))

"""
