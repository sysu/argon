# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from chaofeng import Server,g
from chaofeng.g import mark,static
import login,user,menu
import config

if __name__ == '__main__' :
    s = Server(mark[config.root])
    s.run()
