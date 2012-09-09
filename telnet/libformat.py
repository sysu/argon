#!/usr/bin/python2
# -*- coding: utf-8 -*-
import re
import chaofeng.ascii as ac

t2s = re.compile(r'\[((\d+)(;\d+)*)m')
s2t = re.compile(r'([^`])\[%((\d+)(;\d+)*)#\]')
s2t_close = re.compile(r'\[#%\]([^`])')

quote = re.compile(r'^:.*$', flags=re.M)
quote_author = re.compile(ur'^【 在 .* 中提到: 】$', flags=re.M)
    
def telnet2style(text):
    return t2s.sub(lambda x: u'[%%s#]' % x.group(1), text).replace('[m', '[#%]').replace('\r\n', '\n')

# s2t = re.compile(r'{%((\d+)(;\d+)*)% (.*) %}')
def style2telnet(text):
    text = s2t.sub(lambda x: u'%s\x1b[%sm' % (x.group(1), x.group(2)),
                   text)
    text = s2t_close.sub(lambda x: u'\x1b[m%s' % x.group(1), text)
    text = quote.sub(lambda x : u'[36m%s' % x.group(0), text)
    text = quote_author.sub(lambda x : u'[33;1m%s[m' % x.group(0), text)
    return text#.replace('\n', '\r\n')

def etelnet_to_style(text):
    return text.replace('\r\n', '\n')

def style_to_etelnet(text):
    return text.replace('\n', '\r\n')
