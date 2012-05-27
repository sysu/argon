#!/usr/bin/python2
# -*- coding: utf-8 -*-

class ERROR:

    def __nonzero__(self):
        return False

    def __nonzero__(self):
        return self.key == 0
    
    def __init__(self,key,*content):
        self.content = content
        self.key = key

    def __call__(self,*content):
        return ERROR(self.key,*content)

OK                   = ERROR(0,"OK")

# for register

REG_BAN_ID           = ERROR(1,"Unvaild userid.")
REG_USERID_TOO_SHORT = ERROR(2,"Too short userid.") 
REG_REGISTERED       = ERROR(3,"Registed userid.")
REG_PASSWD_TOO_SHORT = ERROR(4,"Too short password.")

# for login

LOGIN_NO_SUCH_USER   = ERROR(5,"No such user.")
LOGIN_WRONG_PASSWD   = ERROR(6,"Wrong password.")
LOGIN_MAX_LOGIN      = ERROR(7,"Max login.")

def iserror(pack):
    try:
        return isinstance(ERROR,pack)
    except:
        return True
