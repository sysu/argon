# -*- coding: utf-8 -*-

print 'Loading config...'

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

# menu = {
#     "main":[
#         [ u'(E)Group       分类讨论区','sections','e',[13,5]],
#         # ( u'(D)igest       本站精华区',"undone",'d' ),
#         [ u'(F)avourite    个人收藏夹',"favourite",'f' ],
#         # ( u'(R)ecommend    推荐版面区',"undone",'r' ),
#         # ( u'(M)ail         处理信笺区',"undone",'m' ),
#         # ( u'(T)alk         谈天说地区',"undone",'t' ),
#         [ u'(I)nfoEdit   个人资料设定',"user_space",'i' ],
#         [ u'(F)ilm         电影放映室',"movie",'f' ],
#         [ u'(M)ail           处理信笺','mail_menu','m'],
#         # ( u'(S)ervice      特别服务区',"undone",'s' ),
#         # ( u'(C)onfig       系统信息区',"undone",'c' ),
#         # ( u'(P)ersonal     个人文集区',"undone",'p' ),
#         [ u'(H)elp           帮助中心',"help",'h'],
#         [ u'(G)oodbye    离开逸仙时空',"finish",'g' ]
#         ],
#     "main_guest":[
#         [ u'(E)Group       分类讨论区','sections','e',[12,5]],
#         # ( u'(D)igest       本站精华区',"undone",'d' ),
#         # ( u'(R)ecommend    推荐版面区',"undone",'r' ),
#         # ( u'(T)alk         谈天说地区',"undone",'t' ),
#         # ( u'(C)onfig       系统信息区',"undone",'c' ),
#         # ( u'(P)ersonal     个人文集区',"undone",'p' ),
#         [ u'(G)oodbye    离开逸仙时空 ',"finish",'g' ]
#         ],
#     "user_space":[
#         [ u'I) 设定个人资料','user_editdata','i',[12,6]],
#         [ u'P) 修改个人密码','user_change_passwd','p'],
#         [ u'W) 编修个人档案','user_nickdata','w'],
#         [ u'S) 修改签名档','user_edit_sign','s'],
#         [ u'U) 查看我的资料','query_user','u'],
#         [ u'E) 回到主选单','main','e'],],
#     "section":[
#         # dy + append
#         [ u"[1;32mA[0m) 所有讨论区 -- [ALL]",["boardlist",dict(sid=None)],'a',[11,41]],
#         [ u"[1;36mN[0m) 阅读新文章 -- [NEW]","undone",'n'],
#         [ u"[1;36mE[0m) 回到主选单 -- [EXIT]","main",'e'],
#         ],
#     "mail":[
#         [ u"(R)ead          览阅全部信笺", "get_mail", "r", [16,41]],
#         [ u"(S)end          发送站内信件", "send_mail", "s"],
#         [ u"(E)xit          回到主选单",   "main", "e"],
#         ],        
# }

key_maps = {
    "super_key": "a",
    "super_key_2": "r",
    }

default_shortcuts = {
    ac.k_up:"move_up",
    ac.k_down:"move_down",
    ac.k_end:"goto_last",
    ac.k_home:"goto_first",
    ac.k_page_up:"page_up",
    ac.k_page_down:"page_down",
    ac.k_ctrl_l:"refresh",
    ac.k_ctrl_c:"cancel",
    'h':"help",
    }

TABLE_KEY_MAPS = {
    ac.k_up : "move_up",
    ac.k_down : "move_down",
    ac.k_page_down : "page_down",
    ac.k_page_up : "page_up",
    ac.k_home : "goto_first",
    ac.k_end : "goto_last",
    ac.k_ctrl_c : "goto_back",
    "h":"show_help",
    "q":"goto_back",
    ac.k_left:"goto_back",
    ac.k_right:"finish",
    }

# userid_char =

str = {
    "PROMPT_INPUT_PASSWD":u"请输入密码：",
    "PROMPT_INPUT_USERID":u"请输入帐号：",
    "PROMPT_GUEST_UNABLE_TO_USER":u"用户名不可用",
    "PROMPT_AUTH_FAILED":u"认证失败，帐号或密码错误。",
    "PROMPT_INPUT_USERID_REG":u'请输入帐号名称 (Enter User ID, leave blank to abort): ',
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
    "BOARD_THEAD_NORMAL":u"[0;1;44m 编号  未读 刊 登 者       日  期      标  题                                         [m",
    "BOARD_THEAD_GMODE":u"[0;1;44m 编号  未读 刊 登 者       日  期      标  题                      [文摘区]           [m",
    "BOARD_THEAD_MMODE":u"[0;1;44m 编号  未读 刊 登 者       日  期      标  题                      [美文区]           [m",
    "BOARD_THEAD_TOPIC":u"[0;1;44m 编号  未读 刊 登 者       日  期      标  题                      [同主题折叠]       [m",
    "BOARD_THEAD_ONETOPIC":u"[0;1;44m 编号  未读 刊 登 者       日  期      标  题                      [主题阅读]         [m",
    "BOARD_THEAD_AUTHOR":u"[0;1;44m 编号  未读 刊 登 者       日  期      标  题                      [同作者阅读]       [m",
    "EDIT_LIST_QUICK_HELP":u"[m加入并生效[[1;32ma[m,[1;32m+[m], 准备移除[[1;32md[m,[1;32m-[m] 应用并刷新[[1;32m^L[m,[1;32mf[m] 离开[[1;32m.[m]",
    "EDIT_LIST_TEAM_THEAD":u"[44;1m    帐号                     帐号                     帐号                    	[m",
    "EDIT_LIST_USERTEAM_THEAD":u"[44;1m    组                       组                       组                      	[m",
    "MAIL_QUICK_HELP":u"[0m离开[[1;32m←[0m,[1;32mq[0m] 选择[[1;32m↑[0m, [1;32m↓[0m] 阅读信件[[1;32m→[0m,[1;32mRtn[0m] 回 信[[1;32mR[0m] 砍信／清除旧信[[1;32md[0m,[1;32mD[0m] 求助[[1;32mh[0m][m",
    "MAIL_THEAD":u"[0;1;44m 编号  发信者       日 期      标题                                                       [m",
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
   }

hotkeys = {
    "g":{
        ac.k_ctrl_c:"goto_back",
        "h":"show_help",
        ac.k_ctrl_be:"goto_history",
        },
    "menu":{
        ac.k_right:"right_or_finish",
        ac.k_left:"left_or_finish",
        },
    "menu_menu":{
        ac.k_down:"move_down",
        ac.k_up:"move_up",
        },
    "table":{
        },
    "g_table":{
        ac.k_up:"move_up",
        ac.k_down:"move_down",
        ac.k_page_up:"page_up",
        ac.k_page_down:"page_down",
        },
    "boardlist":{
        ac.k_ctrl_be:"goto_history",
        '/':'search',         ac.k_right:'finish',
        'q':'goto_back',      'e':'goto_back',        ac.k_left:'goto_back',
        's':'change_sort',           '#':'goto_line',
        ac.k_end:"goto_last",           '$':'goto_last',
        "a":"add_to_fav",  "d":"remove_fav",
        # admin
        ac.k_ctrl_a:'watch_board',
        'X':'set_readonly',
        ac.k_ctrl_e:'change_board_attr',
        # jump
        "h":"show_help", 
        },
    "boardlist_jump":{
        "u":"query_user_iter",
        "l":"get_mail",
        "!":"goodbye",
        },
    "boardlist_table":{
        "k":"move_up",        "j":"move_down",
        'P':'page_up',          ac.k_ctrl_b:'page_up',        'b':'page_up',
        'N':'page_down',        ac.k_ctrl_f:'page_down',      ' ':'page_down',
        ac.k_home:'goto_first',   
        },
    "board":{
        ac.k_ctrl_be:"goto_history",
        "#":"goto_line",
        ac.k_right:"finish", ac.k_left:"goto_back",
        ac.k_ctrl_p:"new_post","E":"edit_post", ac.k_ctrl_r:"reply_to_author",
        ac.k_ctrl_t:"change_mode",
        'g':"set_g_mark",        'm':"set_m_mark",
        ac.k_ctrl_l:"restore",
        "=":"goto_tid", "\\":"goto_tid", ac.k_ctrl_s :"goto_tid", "p":"goto_tid",
        ac.k_ctrl_u:"goto_author",
        "c":"clear_readmark", "K":"set_read", ac.k_ctrl_a:"query_author",
        ac.k_end:"goto_last", "$":"goto_last",
        "T":"edit_title",
        "h":"show_help",
        "_":"set_replyable",
        "d":"del_post",
        "D":"del_post_range",
        ac.k_ctrl_g:"set_g_mode", "-":"set_onetopic_mode",
        "!":"goto_bye",
        ac.k_ctrl_d:"set_deny",
        "s":"change_board", "u":"query_user",
        },
    "board_table":{
        "k":"move_up", "j":"move_down", "P":"page_up", "N":"page_down",
        ac.k_home:"goto_first", 
        },
    "form":{
        ac.k_right:"submit",
        ac.k_left:"goto_back",
        },
    "edit_2ndcmd_start": ac.k_ctrl_u,
    "edit_editor":{
        ac.k_left:"move_left",
        ac.k_right:"move_right",                ac.k_ctrl_v:"move_right",
        ac.k_up:"move_up",                      ac.k_ctrl_p:"move_up",
        ac.k_down:"move_down",                  ac.k_ctrl_n:"move_down",
        ac.k_delete:"delete",
        ac.k_backspace:"backspace",             ac.k_ctrl_h:"backspace",
        ac.k_backspace2:"backspace",
        ac.k_ctrl_l:"restore_screen_iter",
        ac.k_enter_linux:"new_line",
        ac.k_enter_windows:"new_line",
        ac.k_ctrl_k:"kill_to_end",
        ac.k_ctrl_a:"move_beginning_of_line",   ac.k_home:"move_beginning_of_line",
        ac.k_ctrl_e:"move_end_of_line",         ac.k_end:"move_end_of_line",
        ac.k_ctrl_s:"move_beginning_of_file",
        ac.k_ctrl_t:"move_end_of_file",
        ac.esc:"insert_style",
        ac.k_ctrl_b:"page_up",      ac.k_page_up:"page_up",
        ac.k_ctrl_f:"page_down",    ac.k_page_down:"page_down",
        },
    "edit":{
        # ac.k_ctrl_o:"insert_superclip",
        # ac.k_ctrl_i:"copy_to_superclip",
        ac.k_ctrl_w:"finish",        #############
        ac.k_ctrl_x:"finish",
        ac.k_ctrl_q:"show_help",
        ac.k_ctrl_c:"quit_iter",
        },
    "edit_2nd":{
        ac.k_ctrl_u:"exchange_pos",
        ac.k_ctrl_d:"remove_area",
        ac.k_ctrl_m:"insert_style_area",
        ac.k_ctrl_g:"set_mark",
        },
    "view":{
        ac.k_ctrl_be:"goto_history",
        "Q":"goto_back",
        ac.k_left:"goto_back",
        # ac.k_ctrl_u:"goto_link",
        # "h":"jump_from_screen",
        # ac.k_ctrl_a:"jump_man",
        ac.k_ctrl_r:"jump_from_screen",
        "h":"show_help",
        "R":"reply_post",
        "r":"reply_post",
        },
    "view_textbox":{
        ac.k_up : "move_up",
        "k":"move_up",
        ac.k_down : "move_down",
        " ":"move_down",
        ac.k_right:"move_down",
        "j":"move_down",
        ac.k_ctrl_b:"page_up",
        ac.k_page_up:"page_up",
        ac.k_ctrl_f:"page_down",
        ac.k_page_down:"page_down",
        ac.k_right:"page_down",
        ac.k_home:"goto_first",
        ac.k_end:"goto_last",
        "$":"goto_last",
        },
    "view-board":{
        "a":"add_to_fav",
        },
    "maillist":{
        ac.k_ctrl_p:"send_mail",
        "R":"reply",
        ac.k_left:"goto_back", ac.k_right:"finish",
        },
    "maillist_table":{
        "k":"move_up",       "p":"move_up",      
        "j":"move_down",     "n":"move_down",
        "P":"page_up",       "N":"page_down",
        "$":"goto_last",
        },
    "edit_list":{
        "a":"add",
        "d":"remove",
        "+":"add",
        "-":"remove",
        ac.k_ctrl_l:"refresh_items",
        "f":"refresh_items",
        ".":"goto_back",
        ac.k_ctrl_c:"goto_back",
        },
    "edit_list_ui":{
        ac.k_up:"move_up",
        ac.k_down:"move_down",
        ac.k_left:"move_left",
        ac.k_right:"move_right",
        },
    "set_board_deny":{
        "a":"add_deny",
        '.':"goto_back",
        "d":"remove_deny",
        ac.k_ctrl_c:"goto_back",
        ac.k_ctrl_l:"reload",
        }
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

data_pool = {
    }

import _dark as dark
