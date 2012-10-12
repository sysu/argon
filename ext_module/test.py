#!/usr/bin/env python


def main_test():
    import ext_user
    a = ext_user.GetUserRec('PASSWDS', 0)
#    print dir(a)
#    for i in dir(a):
#        if not i.startswith('__'):
#            print i, str(getattr(a, i))
#
    address = a.GetAddress().decode('gb2312')
    realname = a.GetRealname().decode('gb2312')
    username = a.GetRealname().decode('gb2312')
    passwd = a.GetPasswd()

    print 'address %s' % address
    print 'realname %s' % realname
    print 'username %s' % username
    print 'passwd %s' % passwd
    print len(passwd)

if __name__ == '__main__':
    main_test()

