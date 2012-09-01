#!/usr/bin/python2
# -*- coding: utf-8 -*-

import chaofeng.ascii as ac
import re

repbuf = [(re.escape(k), v) for k,v in ac.ASCII_MAP.items()]
repbuf.sort(key=lambda x: len(x[0]), reverse=True)
patttern = re.compile("|".join(x for x,v in repbuf))

def arepr(u):
    return patttern.sub(lambda m: '[31;1m%s[0m' % ac.ASCII_MAP[m.group(0)],
                        u)

if __name__ == '__main__':
    print arepr(u'\x1b[34m你吃饭了吗？')
