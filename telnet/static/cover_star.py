#!/usr/bin/python

import codecs
import traceback
import re

s2t = re.compile(r'\[#((\d+)(;\d+)*)%\]')
s2t_close = re.compile(r'\[%#\]')
def style2telnet(text):
    text = s2t.sub(lambda x: '\x1b[%sm' % x.group(1),
                   text)
    return s2t_close.sub(u'\x1b[m', text)

def cover(filename):
    try:
        with codecs.open(filename, 'r') as f:
            text = f.read()
        text = text.replace('*[', '[')
        text = style2telnet(text)
        with codecs.open(filename, 'w') as f:
            f.write(text)
    except Exception as e:
	traceback.print_exc()
        raw_input('>>')
    else:
        print 'CORVER %s ' % filename

if __name__ == '__main__' :
    import sys
    for f in sys.argv[1:] :
        cover(f)
