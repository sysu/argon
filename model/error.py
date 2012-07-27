#!/usr/bin/python2
# -*- coding: utf-8 -*-

class ArgonException(Exception): pass

class TooFrequentException(ArgonException): pass

# for register

class RegistedError(ArgonException):
    BAN_ID = (1,"Unvaild userid.")
    USERID_TOO_SHORT = (2,"Too short userid.") 
    REGISTERED       = (3,"Registed userid.")
    PASSWD_TOO_SHORT = (4,"Too short password.")

class LoginError(ArgonException):
    NO_SUCH_USER   = (5,"No such user.")
    WRONG_PASSWD   = (6,"Wrong password.")
    MAX_LOGIN      = (7,"Max login.")
