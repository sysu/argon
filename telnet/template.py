# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from jinja2 import Environment
from chaofeng import ascii as ac
from model import manager
from chaofeng.g import static

def ascii_format(source,background=None,font=None):
    return '%s%s%s%s' % (ac.background[background],
                       ac.font[font],source,ac.reset)

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

def ctime(source):
    pass

RENDER_FILTERS = {
    "uid":userid2uid,
    "user_attr":userid2info,
    "wrapper":ascii_wrapper,
    "art":ascii_format,
    "bid2boardname":bid2boardname,
    "ctime":ctime,
    }

RENDER_TESTS = {}

RENDER_GLOBALS = {
    "manager":manager,
    "ac":ac,
    "BBS_HOST_FULLNAME":u"逸仙时空 Yat-Sen Channel argo.sysu.edu.cn",
    "o_o":ac.outlook,
    }

def load_jinjatxt(f):
    raw = f.read()
    t = render.from_string(raw).render()
    print t
    return t

def load_jinjatpl(f):
    raw = f.read()
    return render.from_string(raw)

render = Environment(newline_sequence="\r\n",
                  autoescape=False)

render.filters.update(RENDER_FILTERS)
render.tests.update(RENDER_TESTS)
render.globals.update(RENDER_GLOBALS)
render.globals.update(ac.art_code)

