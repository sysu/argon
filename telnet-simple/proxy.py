#!/usr/bin/python2
import telnetlib
argo = telnetlib.Telnet('argo.sysu.edu.cn')

import socket

# Echo server program
import socket

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 5000              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connected by', addr

import time

while True:
    data = conn.recv(1024)
    argo.write(data)
    time.sleep(0.1)
    re = argo.read_very_eager()

    conn.sendall(re)

    print '%s%r' % ('*' * 20,data)
    print
    print '%r' % re
    print
    print '%s' % '*'*20
        
# output(get_remote(''))
output(get_remote(''))
while 1:
    data = conn.recv(1024)
    output(get_remote(data))

conn.close()
