# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from jinja2 import Environment,FileSystemLoader
from chaofeng import ascii as ac
from model import manager
from datetime import datetime
# from chaofeng.g import static

def ascii_format(source,background=None,font=None):
    return '%s%s%s%s' % (ac.background[background],
                       ac.font[font],source,ac.reset)

def ascii_width(source,width):
    return ('%*s' % (width, str(source).encode('gbk'))).decode('gbk')

def ascii_wrapper(source,*wrapper):
    return '\x1b[%sm%s\x1b[0m' % (';'.join(wrapper),source)

def get_user(uid):
    return manager.userinfo.get_user(uid)

def userid2uid(userid):
    return manager.name2id(userid)

def userid2info(userid,attr):
    res = manager.userinfo.select_attr(userid, attr)
    return res and res[attr]

def bid2boardname(bid):
    return manager.board.id2name(bid)

def current_ctime():
    return datetime.now().ctime()

RENDER_FILTERS = {
    "uid":userid2uid,
    "user_attr":userid2info,
    "wrapper":ascii_wrapper,
    "art":ascii_format,
    "bid2boardname":bid2boardname,
    "width":ascii_width,
    }

RENDER_TESTS = {}

RENDER_GLOBALS = {
    "manager":manager,
    "ac":ac,
    "BBS_HOST_FULLNAME":u"逸仙时空 Yat-Sen Channel argo.sysu.edu.cn",
    "o_o":ac.outlook,
    "delay":ac.delay,
    "current":current_ctime,
    }

env = Environment(loader=FileSystemLoader('./static'),
                  newline_sequence="\r\n",
                  autoescape=False)

env.filters.update(RENDER_FILTERS)
env.tests.update(RENDER_TESTS)
env.globals.update(RENDER_GLOBALS)
env.globals.update(ac.art_code)

