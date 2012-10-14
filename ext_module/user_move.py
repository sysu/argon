#!/usr/bin/env python
# encoding: utf-8

import sys
sys.path.append('..')

import ext_user, bcrypt, time
from hashlib import md5
from model import manager as mgr

dec_code = 'gb18030'

def ts2dt(ts):
    ltime = time.localtime(ts)
    timeStr = time.strftime("%Y-%m-%d %H:%M:%S", ltime)
    return timeStr

def main_process():
    recfile = 'PASSWDS'
    num = -1
    fail_cnt = 0
    fp = open('fail.lst', 'w') 
    while True:
        num += 1
        try:
            urec = ext_user.GetUserRec(recfile, num)
            if not urec.userid: continue

            print num, urec.userid
            # Use new passwd encryption  
            if len(urec.passwd) > 13: # md5
                new_passwd = bcrypt.hashpw(urec.GetPasswd(), bcrypt.gensalt(10))
            else:
                new_passwd = urec.passwd
            try:
                mgr.userinfo.add_user(
                        userid = urec.userid,
                        passwd = new_passwd,
                        username = urec.GetUsername().decode(dec_code),
                        email = str(urec.email).decode(dec_code),
                        remail = urec.reginfo, #认证email
                        netid = urec.reginfo,

                        firstlogin = ts2dt(urec.firstlogin),
                        firsthost = urec.ident,
                        lastlogin = ts2dt(urec.lastlogin),
                        lasthost = urec.lasthost,
                        lastlogout = ts2dt(urec.lastlogout),

                        numlogins = urec.numlogins,
                        numposts = urec.numposts,
                        stay = urec.stay,

                        birthday = '%d-%d-%d ' % (urec.birthyear, urec.birthmonth,
                            urec.birthday),

                        address = urec.GetAddress().decode(dec_code),
                        usertitle = urec.usertitle,
                        gender = 1 if urec.gender == 'M' else 0,
                        realname = urec.GetRealname().decode(dec_code)
                        )
                print num, urec.userid
            except:
                fp.write('%s\n' % urec.userid)
                fail_cnt += 1

        except AttributeError, e:
            print e
            break
    fp.close()
    print 'total fail: %d' % fail_cnt

if __name__ == '__main__':
    main_process()

