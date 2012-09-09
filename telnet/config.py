# -*- coding: utf-8 -*-

import logging

logging.info('Loading config...')

from chaofeng import ascii as ac
import yaml
# from chaofeng.g import static
# from template import load_jinjatxt,load_jinjatpl

import os, sys

BASEPATH_TELNET = os.path.dirname(os.path.realpath(__file__))
BASEPATH = os.path.dirname(BASEPATH_TELNET)

BBS_HOST_FULLNAME = u"逸仙时空 Yat-Sen Channel"
BBS_HOST_DOMAIN = u"argo.sysu.edu.cn"

with open("filelist.yaml") as f:
    all_static_file = yaml.load(f)

with open("filelist_help.yaml") as f:
    all_help_file = yaml.load(f)

letter = [
    'register', 'register_succ',
    ]

# 菜单的设定
# 第一项是一个字符串，将会显示到屏幕。第二项是跳转的页面的mark，和goto的参数。
# 第三项是快捷键。第四项是显示的坐标，如果没有则是上一列x,y+1

with open('data.yaml') as f:
    data = yaml.load(f)

with open('menu.yaml') as f:
    menu = yaml.load(f)

# data = {
#     "MAX_TRY_LOGIN_TIME":50,
#     "MAX_TRY_REGISTER_TIME":150,
#     "MAX_STACK_DEEP":5,
#     "MAX_HISTORY_DEEP":20,
#     'ROOT':'welcome',
#     }

str = {
    "PROMPT_INPUT_PASSWD":u"请输入密码：",
    "PROMPT_INPUT_USERID":u"请输入帐号：",
    "PROMPT_GUEST_UNABLE_TO_USE":u"抱歉，暂时不支持游客登录！\r\n",
    "PROMPT_AUTH_FAILED":u"认证失败，帐号或密码错误。",
    "PROMPT_INPUT_USERID_REG":u'请输入帐号名称 (Enter User ID, leave blank to abort):\r\n',
    "PROMPT_INPUT_PASSWD_REG":u'请设定您的密码 (Setup Password): ',
    "PROMPT_REG_SUCC":u"成功",
    "PROMPT_REG_CANNOT_USE":u"抱歉，您不能使用该id。请再拟。",
    "PROMPT_REG_USERID_TOO_SHORT":u"抱歉，您的id太短撩。 请再拟。",
    "PROMPT_REG_REGISTERED":u"抱歉，您的id已经被注册了。 请再拟。",
    "PROMPT_REG_PASSWD_TOO_SHORT":u"密码太短了，请大于6位。",
    "PROMPT_CANCEL":u'\r\n你按下了Ctrl+C ，将会取消本次的活动。\r\n :-) 别害怕，你可以再来一次。',
    "BOARDLIST_QUICK_HELP":u"[0m 主选单[[1;32m←[0m,[1;32mq[0m] 阅读[[1;32m→[0m,[1;32mRtn[0m] 选择[[1;32m↑[0m,[1;32m↓[0m]  求助[[1;32mh][m",
    "BOARDLIST_THEAD":u"[0;1;44m 编号   讨论区名称           中 文 叙 述         在线  全部  版主                [m",
    "BOARD_QUICK_HELP":u"[0m离开[[1;32m←[0m,[1;32mq[0m] 选择[[1;32m↑[0m,[1;32m↓[0m] 阅读[[1;32m→[0m,[1;32mRtn[0m] 发表文章[[1;32mCtrl-P[0m] 求助[[1;32mh[0m][m",
    "BOARD_THEAD":u"[0;1;44m 编号  未读 刊 登 者       日  期      标  题                                         [m",
    "BOARD_g_MODE_THEAD":u"[0;1;44m 编号  未读 刊 登 者       日  期      标  题                      [文摘区]           [m",
    "BOARD_m_MODE_THEAD":u"[0;1;44m 编号  未读 刊 登 者       日  期      标  题                      [美文区]           [m",
    "BOARD_o_MODE_THEAD":u"[0;1;44m 编号  未读 刊 登 者       日  期      标  题                      [同主题折叠]       [m",
    "BOARD_t_MODE_THEAD":u"[0;1;44m 编号  未读 刊 登 者       日  期      标  题                      [主题阅读]         [m",
    "BOARD_u_MODE_THEAD":u"[0;1;44m 编号  未读 刊 登 者       日  期      标  题                      [同作者阅读]       [m",
    "EDIT_LIST_QUICK_HELP":u"[m加入并生效[[1;32ma[m,[1;32m+[m], 准备移除[[1;32md[m,[1;32m-[m] 应用并刷新[[1;32m^L[m,[1;32mf[m] 离开[[1;32m.[m]",
    "EDIT_LIST_TEAM_THEAD":u"[44;1m    帐号                     帐号                     帐号                    	[m",
    "EDIT_LIST_USERTEAM_THEAD":u"[44;1m    组                       组                       组                      	[m",
    "MAILLIST_QUICK_HELP":u"[0m离开[[1;32m←[0m,[1;32mq[0m] 选择[[1;32m↑[0m, [1;32m↓[0m] 阅读信件[[1;32m→[0m,[1;32mRtn[0m] 回 信[[1;32mR[0m] 砍信／清除旧信[[1;32md[0m,[1;32mD[0m] 求助[[1;32mh[0m][m",
    "MAILLIST_THEAD":u"[0;1;44m 编号  发信者       日 期      标题                                                       [m",
    'MSG_BOARDLIST_MODE_0':u'按讨论区编号排序',
    'MSG_BOARDLIST_MODE_1':u'按在线人数排序',
    'MSG_BOARDLIST_MODE_2':u'按讨论区名称排序',
    'MSG_BOARDLIST_MODE_3':u'按中文描述排序',
    'MSG_BOARD_MODE_NORMAL':u'切换一般模式',
    'MSG_BOARD_MODE_GMODE':u'阅读带g标记的文章',
    'MSG_BOARD_MODE_MMODE':u'阅读带m标记的文章',
    'MSG_BOARD_MODE_TOPIC':u'只看主题贴',
    'MSG_BOARD_MODE_ONETOPIC':u'查看单一主题',
    'MSG_BOARD_MODE_AUTHOR':u'查看单一作者',
    'FORM_QUICK_HELP':u'[0m返回[[1;32m←[0m,[1;32mq[0m] 修改[[1;32m→[0m,[1;32mRtn[0m] 选择[[1;32m↑[0m,[1;32m↓[0m] 求助[[1;32mh[0m][m',
    'FORM_THEAD':u'[0;1;44m  项目名称                         项目属性                                   [m',
    'DENY_QUICK_HELP' : u'[m封禁[[32;1ma[m] 解除封禁[[32;1md[m] 返回[[32;1m.[m]',
    'DENY_THEAD' : u'[0;1;44m 流水号  封禁日期      被封者        被封原因                                 [m',
    'USERONLINE_QUICK_HELP' : u'查看用户[[32;1m→[m,[32;1mRtn[m] 返回[[32;1m←[m] 发站内信[[32;1ms[m]',
    'USERONLINE_THEAD' : u'[0;1;44m          账号              昵称               地址              状态                [m',
   }

user_options = {
    "nickdata":{
        "shai":u"晒一下",
        "contact":u"联系方式",
        "want":u"想要的东西",
        "job":u"工作",
        "marriage":u"婚恋状况",
        "about":u"个人说明档",
        }
    }

mark2zhname = {
    'main' : u'主选单',
    'mail' : u'处理信笺区',
    'user_space': u'个人资料设定',
    'sys_admin': u'系统属性设置',
    'boardlist': u'[讨论区列表]',
    'get_mail': u'邮件选单',
    }

import _dark as dark

shortcuts = {
    'menu':{
        ac.k_right:"_right_or_finish",
        ac.k_left:"_left_or_finish",
        'h':'show_help',
        },
    'menu_ui':{
        ac.k_down:"move_down",
        ac.k_up:"move_up",
        },
    'boardlist':{
        "/":"_search",        "s":"_change_sort",   
        "q":"goto_back",      "e":"goto_back",         ac.k_left:"goto_back",
        "#":"_goto_line",     ac.k_ctrl_y:"post_bug",
        "u":"fgo_query_user_iter",    "l":"fgo_get_mail",    "!":"fgo_bye",
        'h':'show_help',
        },
    'boardlist_ui':{
        "k":"move_up",        ac.k_up:"move_up",
        "j":"move_down",      ac.k_down:"move_down",
        'P':'page_up',          ac.k_ctrl_b:'page_up',
        ac.k_page_up:"page_up", 'b':'page_up',
        'N':'page_down',            ac.k_ctrl_f:'page_down',
        ac.k_page_down:"page_down", ' ':'page_down',
        ac.k_home:'goto_first',     "$":"goto_last",
        ac.k_end:"goto_last",
        },
    'boardlist_fetch_do':{
        ac.k_ctrl_a : "query_board",
        ac.k_ctrl_e : "change_board_attr",
        "a":"add_to_fav",      "d":"remove_fav",
        ac.k_right:"enter_board",
        "x":"set_readonly",
        },
    
    'board':{
        "s":"change_board", ac.k_ctrl_p:"new_post",
        # ac.k_ctrl_r:"reply_to_authoer",  
        "D":"del_post_range", "c":"clear_readmark",
        ac.k_ctrl_d:"goto_set_deny",
        ac.k_ctrl_t:"goto_filter_mode",
        ac.k_ctrl_g:"goto_filter_g",
        ac.k_ctrl_y:"goto_filter_o",
        "=":"goto_filter_tid", "\\":"goto_filter_tid",
        ac.k_ctrl_s :"goto_filter_tid", "p":"goto_filter_tid",
        ac.k_ctrl_u:"goto_filter_author",
        ac.k_left:"goto_back",
        "#":"_goto_line",
        "l":"fgo_get_mail",    "!":"fgo_bye",
        'h':'show_help',
        "W":"set_board_info",
        },
    'board_filter':{
        ac.k_ctrl_p:"new_post",
        # ac.k_ctrl_r:"reply_to_authoer",  
        "#":"_goto_line",
        ac.k_ctrl_d:"goto_set_deny",
        ac.k_left:"goto_back",        
        },
    'board_ui':{
        ac.k_up:"move_up",  "k":"move_up",
        ac.k_down:"move_down", "j":"move_down",
        "P":"page_up", "N":"page_down",
        ac.k_page_up : "page_up", ac.k_page_down:"page_down", " ":"page_down",
        ac.k_home:"goto_first", "$":"goto_last", ac.k_end:"goto_last",
        },
    'board_fetch':{
        "d":"del_post",      ac.k_ctrl_a:"goto_query_user",
        ac.k_ctrl_r:"reply_post", ac.k_right:"next_frame",
        ac.k_ctrl_c:"repost",
        'r':"reply_post",
        "R":"reply_post",
        },
    'board_update':{
        "E":"edit_post",
        "t":"edit_title",    "T":"edit_title",
        "K":"set_read",      "g":"set_g_mark",
        "m":"set_m_mark",    "_":"set_replyable",
        },
    "edit_ui":{
        ac.k_left:"move_left",
        ac.k_right:"move_right",                ac.k_ctrl_v:"move_right",
        ac.k_up:"move_up",                      ac.k_ctrl_p:"move_up",
        ac.k_down:"move_down",                  ac.k_ctrl_n:"move_down",
        ac.k_delete:"delete",                   ac.k_ctrl_d:"delete",
        ac.k_backspace:"backspace",             ac.k_ctrl_h:"backspace",
        ac.k_backspace2:"backspace",
        ac.k_ctrl_l:"restore_screen_iter",
        ac.k_enter_linux:"new_line",
        ac.k_enter_windows:"new_line",
        ac.k_ctrl_k:"kill_to_end",
        ac.k_ctrl_a:"move_beginning_of_line",
        ac.k_home:"move_beginning_of_line",
        ac.k_ctrl_e:"move_end_of_line",         ac.k_end:"move_end_of_line",
        ac.k_ctrl_s:"move_beginning_of_file",
        ac.k_ctrl_t:"move_end_of_file",
        ac.esc:"insert_style",
        ac.k_ctrl_b:"page_up",      ac.k_page_up:"page_up",
        ac.k_ctrl_f:"page_down",    ac.k_page_down:"page_down",
        ac.k_ctrl_y:"kill_whole_line",
        },
    "edit_ui_2nd":{
        ac.k_ctrl_u: "exchange_pos",
        ac.k_ctrl_d: "remove_area",
        ac.k_ctrl_m: "set_mark",
        }
    }
