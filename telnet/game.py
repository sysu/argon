#!/usr/bin/python2
# -*- coding: utf-8 -*-

from libframe import BaseAuthedFrame
import chaofeng.ascii as ac
from chaofeng.g import mark
from model import manager

@mark('game_guess_number')
class GuessNumber(BaseAuthedFrame):

    gn_numbers = dict()
    gn_users = set()
    gn_max_user = 50
    
    def initialize(self):
        self.write(ac.clear)        
        if self.userid in self.gn_users :
            self.writeln(u'你已经埋过一次数字了！')
            self.pause()
            self.goto_back()
        num = self.readline(prompt=u'要埋什么数字？', buf_size=8, acceptable=ac.isdigit)
        if num :
            d = int(num)
            if d in self.gn_numbers :
                self.writeln(u'\r\n撒花，你埋的数字和 %s 的一样！' % self.gn_numbers[d])
                letter1 = self.render_letter(fuser=self.userid, tuser=self.gn_numbers[d], number=d)
                letter2 = self.render_letter(fuser=self.gn_numbers[d], tuser=self.userid, number=d)
                manager.action.send_mail(fromuserid=u'猜数字之神', touserid=self.userid,
                                  title=u'你埋的数字中啦！', content=letter1)
                manager.action.send_mail(fromuserid=u'猜数字之神', touserid=self.gn_numbers[d],
                                  title=u'你埋的数字中啦！', content=letter2)
                del self.gn_numbers[d]
            else:
                if len(self.gn_users) > self.gn_max_user :
                    self.reset()
                self.gn_numbers[d] = self.userid
                self.writeln(u'埋下了你的数字！')
            self.gn_users.add(self.userid)
            self.pause()
            self.goto_back()

    @classmethod
    def reset(cls):
        cls.gn_numbers = dict()
        cls.gn_users = dict()

    def render_letter(self, fuser, tuser, number):
        return self.render_str('letter/game_guess_number_match',
                               fuser=fuser, tuser=tuser, number=number)
