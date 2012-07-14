# -*- coding: utf-8 -*-
from chaofeng import ascii as ac
# from chaofeng.g import static
# from template import load_jinjatxt,load_jinjatpl

BBS_HOST_FULLNAME = u"逸仙时空 Yat-Sen Channel"
BBS_HOST_DOMAIN = u"argo.sysu.edu.cn"


class Config(dict):
    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            return dict()

chaofeng = Config(
    static={
        "loader":{
            # '.jtxt':load_jinjatxt,
            # '.jtpl':load_jinjatpl,
            }
        }
    )
# static.config(**chaofeng.static)

for key in ['board','help','menu_sections','menu_board','view',
             'boardlist','index','menu_main','testjump','edit'] :
    # static.load('help/%s' % key)
    pass

root = 'welcome'

# 菜单的设定
# 第一项是一个字符串，将会显示到屏幕。第二项是跳转的页面的mark，和goto的参数。
# 第三项是快捷键。第四项是显示的坐标，如果没有则是上一列x,y+1

menu = {
    "main":(
        ( u'(E)Group       分类讨论区','sections','e',(12,5)),
        # ( u'(D)igest       本站精华区',"undone",'d' ),
        # ( u'(F)avourite    个人收藏夹',"undone",'f' ),
        # ( u'(R)ecommend    推荐版面区',"undone",'r' ),
        # ( u'(M)ail         处理信笺区',"undone",'m' ),
        # ( u'(T)alk         谈天说地区',"undone",'t' ),
        # ( u'(I)nfoEdit     个人工具箱',"user_space",'i' ),
        # ( u'(S)ervice      特别服务区',"undone",'s' ),
        # ( u'(C)onfig       系统信息区',"undone",'c' ),
        # ( u'(P)ersonal     个人文集区',"undone",'p' ),
        ( u'(G)oodbye    离开逸仙时空',"finish",'g' )
        ),
    "main_guest":(
        ( u'(E)Group       分类讨论区','sections','e',(12,5)),
        # ( u'(D)igest       本站精华区',"undone",'d' ),
        # ( u'(R)ecommend    推荐版面区',"undone",'r' ),
        # ( u'(T)alk         谈天说地区',"undone",'t' ),
        # ( u'(C)onfig       系统信息区',"undone",'c' ),
        # ( u'(P)ersonal     个人文集区',"undone",'p' ),
        ( u'(G)oodbye    离开逸仙时空 ',"finish",'g' )
        ),
    "userspace":(
        ( u'I) 设定个人资料','user_edit_data','i',(12,4)),
        ( u'P) 修改个人密码','change_passwd','p'),
        ( u'W) 编修个人档案','undone','w'),
        ( u'E) 回到主选单','main','e'),),
    "section":(
        # dy + append
        ( u"[1;32mA[0m) 所有讨论区 -- [ALL]",("boardlist",dict(sid=None)),'a',(11,41)),
        ( u"[1;36mN[0m) 阅读新文章 -- [NEW]","undone",'n'),
        ( u"[1;36mE[0m) 回到主选单 -- [EXIT]","main",'e'),
        )
}

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
    ac.k_home : "go_first",
    ac.k_end : "go_last",
    ac.k_ctrl_c : "goto_back",
    "h":"show_help",
    "q":"goto_back",
    ac.k_left:"goto_back",
    ac.k_right:"finish",
    }

# userid_char =

max_try_login_time = 50
max_try_register_time = 150
max_stack_deep = 5
max_history_deep = 20

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
    "BOARDLIST_QUICK_HELP":u"[0m[I 主选单[[1;32m←[0m,[1;32mq[0m] 阅读[[1;32m→[0m,[1;32mRtn[0m] 选择[[1;32m↑[0m,[1;32m↓[0m]  求助[[1;32mh][m",
    "BOARDLIST_THEAD":u"[0;1;44m[I 编号  讨论区名称           中 文 叙 述         在线  全部  属性  版主          [m"
   }

hotkeys = {
    "g":{
        ac.k_ctrl_c:"goto_back",
        "h":"show_help",
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
    "table_table":{
        ac.k_up:"move_up",
        ac.k_down:"move_down",
        ac.k_page_up:"page_up",
        ac.k_page_down:"page_down",
        },
    "boardlist":{
        '/':'search',         ac.k_right:'finish',
        'q':'goto_back',      'e':'goto_back',        ac.k_left:'goto_back',
        's':'change_sort',
        # admin
        ac.k_ctrl_a:'watch_board',
        'X':'set_readonly',
        ac.k_ctrl_e:'change_board_attr',
        },
    "boardlist_table":{
        "k":"move_uo",        "j":"move_down",
        'P':'page_up',          ac.k_ctrl_b:'page_up',        'b':'page_up',
        'N':'page_down',        ac.k_ctrl_f:'page_down',      ' ':'page_down',
        ac.k_home:'go_first',   ac.k_end:"go_last",           '$':'go_last',
        '#':'go_line',
        },
    }
