import re
import chaofeng.ascii as ac

t2s = re.compile(r'\*\[((\d+)(;\d+)*)m')
s2t = re.compile(r'\[#((\d+)(;\d+)*)%\]')
    
def telnet2style(text):
    return t2s.sub(lambda x: u'[#%s%%]' % x.group(1), text)

# s2t = re.compile(r'{%((\d+)(;\d+)*)% (.*) %}')
def style2telnet(text):
    return s2t.sub(lambda x: '\x1b[%sm' % x.group(1),
                   text).replace('[%#]', ac.reset)
