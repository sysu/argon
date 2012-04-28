#!/usr/bin/env python

from Model import Model

m = Model()

m.connect()
m.query("show tables")
print m.fetchall()

m.closedb()
