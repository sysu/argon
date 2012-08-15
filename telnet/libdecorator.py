#!/usr/bin/python2
# -*- coding: utf-8 -*-

from model import manager
from functools import wraps

def need_perm(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        p = self.check_perm(*args, **kwargs)
        if p is True:
            return f(self, *args, **kwargs)
        else:
            self.writeln(p)
            self.pause()
            self.goto_back()
    return wrapper

def need_perm_checker(checker):
    def inner(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            p = checker(self, *args, **kwargs)
            if p is True:
                return f(self, *args, **kwargs)
            else:
                self.writeln(p)
                self.pause()
                self.goto_back()
        return wrapper
    return inner
