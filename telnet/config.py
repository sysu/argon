# -*- coding: utf-8 -*-
from chaofeng import ascii as ac

root = 'welcome'

# 菜单的设定
# 第一项是一个字符串，将会显示到屏幕。第二项是跳转的页面的mark，和goto的参数。
# 第三项是快捷键。第四项是显示的坐标，如果没有则是上一列x,y+1

menu = {
    "main":(
        ( u'(E)Group       分类讨论区','section_menu','e',(12,5)),
        # ( u'(D)igest       本站精华区',"undone",'d' ),
        # ( u'(F)avourite    个人收藏夹',"undone",'f' ),
        # ( u'(R)ecommend    推荐版面区',"undone",'r' ),
        # ( u'(M)ail         处理信笺区',"undone",'m' ),
        # ( u'(T)alk         谈天说地区',"undone",'t' ),
        # ( u'(I)nfoEdit     个人工具箱',"user_space",'i' ),
        # ( u'(S)ervice      特别服务区',"undone",'s' ),
        # ( u'(C)onfig       系统信息区',"undone",'c' ),
        # ( u'(P)ersonal     个人文集区',"undone",'p' ),
        ( u'(G)oodbye    离开逸仙时空',"bye",'g' )
        ),
    "main_guest":(
        ( u'(E)Group       分类讨论区','section_menu','e',(12,5)),
        # ( u'(D)igest       本站精华区',"undone",'d' ),
        # ( u'(R)ecommend    推荐版面区',"undone",'r' ),
        # ( u'(T)alk         谈天说地区',"undone",'t' ),
        # ( u'(C)onfig       系统信息区',"undone",'c' ),
        # ( u'(P)ersonal     个人文集区',"undone",'p' ),
        ( u'(G)oodbye    离开逸仙时空 ',"bye",'g' )
        ),
    "userspace":(
        ( u'I) 设定个人资料','user_edit_data','i',(12,4)),
        ( u'P) 修改个人密码','change_passwd','p'),
        ( u'W) 编修个人档案','undone','w'),
        ( u'E) 回到主选单','main','e'),),
    "section":(
        # dy + append
        ( u"[1;32mA[0m) 所有讨论区 -- [ALL]",("boardlist",{"section_name":True}),'a',(11,41)),
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
