# -*- coding: utf-8 -*-

from chaofeng import Server,g
from chaofeng.g import mark,static
import config
import frame

if __name__ == '__main__' :
    s = Server(mark[config.root])
    s.run()
