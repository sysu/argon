import re
import chaofeng.ascii as ac

t2s = re.compile(r'\[((\d+)(;\d+)*)m')
s2t = re.compile(r'([^`])\[#((\d+)(;\d+)*)%\]')
s2t_close = re.compile(r'\[%#\]([^`])')
    
def telnet2style(text):
    return t2s.sub(lambda x: u'[#%s%%]' % x.group(1), text).replace('[m', '[%#]')

# s2t = re.compile(r'{%((\d+)(;\d+)*)% (.*) %}')
def style2telnet(text):
    text = s2t.sub(lambda x: u'%s\x1b[%sm' % (x.group(1), x.group(2)),
                   text)
    return s2t_close.sub(lambda x: u'\x1b[m%s' % x.group(1), text)
