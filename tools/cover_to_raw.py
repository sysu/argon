#!/usr/bin/python

import sys
sys.path.append('../telnet/')

from libformat import *
import codecs

def cover_to_raw(filename):
    with codecs.open(filename, encoding='utf8') as f:
        text = style2telnet(f.read())
    with codecs.open(filename, 'w', encoding='utf8') as f:
        f.write(text)

if __name__ == '__main__':
    for f in sys.argv[1:]:
        try:
            cover_to_raw(f)
        except:
            import traceback
            traceback.print_exc()
