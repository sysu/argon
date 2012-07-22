#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')
from model import manager as mgr


def fun_gen_quote(userid, content):
    
    max_quote_line = 5

    owner = mgr.userinfo.get_user(userid)
    if not owner: owner['userid'] = owner['nickname'] = 'null' 

    pattern = u'【 在 %s ( %s ) 的大作中提到: 】' % \
                ( owner['userid'], owner['nickname'] )

    quote = pattern + '\n' + '\n'.join(map(lambda l: u'：'+l, content.split('\n')[:max_quote_line]))

    return quote

