#!/usr/bin/python2
# -*- coding: utf-8 -*-

from chaofeng.g import mark
from edit import BaseEditFrame
from view import BaseTextBoxFrame
from model import manager
import re

inv_re = re.compile(r'@(\w{3,20}) ')
def find_all_invert(content):
    return inv_re.findall(content)

@mark('notice_box')
class NoticeBoxFrame(BaseTextBoxFrame):

    def initialize(self):
        manager.status.set_status(self.seid,
                                  manager.status.POSTING)
        self.total = int(manager.notify.check_notice_notify(self.userid) or 0)
        manager.notify.clear_notice_notify(self.userid)
        notices = manager.notice.get_notice(self.userid,
                                            0 ,10)
        text = self.render_str('notice_box', notices=notices,
                               total=self.total)
        self.setup(text=text)

    def finish(self, e=None):
        self.goto_back()

@BaseEditFrame.plugin.hook_up('after_publish_new_post')
def push_to_inve(frame, pid, attrs, text):
    invs = find_all_invert(text)
    if len(invs) >= 10:
        frame.message(u'你@太多人啦！')
        self.pause()
    else:
        userids = []
        for u in invs:
            user = manager.userinfo.get_user(u)
            if user :
                userids.append(user['userid'])
        manager.notice.add_inve(frame.userid,
                                attrs['boardname'],
                                pid, userids)
        for u in userids:
            manager.notify.add_notice_notify(u)
