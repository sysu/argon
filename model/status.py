#!/usr/bin/python2
# -*- coding: utf-8 -*-

status_display = {
    'BUGREPORT' : u'报告错误',
    
    'IDLE' : u'', 
    # 'NEW' : u'新站友注册', 
    'LOGIN' : u'进入本站', 
    'DIGESTRACE' : u'浏览精华区', 
    'MMENU' : u'主选单', 
    'ADMIN' : u'管理者选单', 
    'SELECT' : u'选择讨论区', 
    'READBRD' : u'一览众山小', 
    'READNEW' : u'看看新文章', 
    'READING' : u'品味文章',
    'RHELP' : u'查看帮助',
    'POSTING' : u'文豪挥笔', 
    'MAIL' : u'处理信笺',
    'NOTICE' : u'查看消息',
    'SMAIL' : u'寄语信鸽', 
    'RMAIL' : u'阅览信笺', 
    'TMENU' : u'聊天选单', 
    'LUSERS' : u'东张西望:)', 
    'FRIEND' : u'寻找好友', 
    'MONITOR' : u'探视民情', 
    'QUERY' : u'查询网友', 
    'TALK' : u'聊天', 
    'PAGE' : u'呼叫', 
    'CHAT1' : u'国际会议厅', 
    'CHAT2' : u'咖啡红茶馆', 
    'CHAT3' : u'Chat3', 
    'CHAT4' : u'Chat4', 
    'LAUSERS' : u'探视网友', 
    'XMENU' : u'系统资讯', 
    'VOTING' : u'投票中...',
    'EDITUFILE' : u'编辑个人档', 
    'EDITSFILE' : u'编修系统档', 
    'ZAP' : u'订阅讨论区', 
    'SYSINFO' : u'检查系统', 
    'DICT' : u'翻查字典', 
    'LOCKSCREEN' : u'屏幕锁定', 
    'NOTEPAD' : u'留言板', 
    'GMENU' : u'工具箱', 
    'MSG' : u'送讯息', 
    'USERDEF' : u'自订参数', 
    'EDIT' : u'修改文章', 
    'OFFLINE' : u'自杀中..', 
    'EDITANN' : u'编修精华', 
    'LOOKMSGS' : u'察看讯息', 
    'WFRIEND' : u'寻人名册', 
    'WNOTEPAD' : u'欲走还留', 
    'BBSNET' : u'BBSNET',
    'WINMINE' : u'键盘扫雷', 
    'FIVE' : u'决战五子棋', 
    'PAGE_FIVE' : u'邀请下棋', 
    'DEFAULT' : u'扑朔迷离',
    }

class Holder(object):
    pass

status = Holder()

import sys
module = sys.modules[__name__]
for key in status_display:
    setattr(module, key, key)

