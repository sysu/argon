import telnetlib
import select
import sys
from time import sleep
from time import sleep

REMOTE = 'localhost'
PORT = 5000

tn = telnetlib.Telnet(REMOTE, port=PORT)
sys.stdout.write(tn.read_very_eager())
sys.stdout.flush()
sleep(0)
tn.write('admin\n123456\ne\n')
while 1:
    rfd, wfd, xfd = select.select([tn, sys.stdin], [], [])
    if tn in rfd:
        text=tn.read_very_eager()
        if text:
            sys.stdout.write(text)
            sys.stdout.flush()
    if sys.stdin in rfd:
        line = sys.stdin.readline()
        if not line:
            break
        tn.write(line)

