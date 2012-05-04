# -*- coding: utf-8 -*-
from chaofeng import ascii

root = 'welcome'

menu = {
    "main":(
        ( u'(E)Group       分类讨论区',('section_menu',{}),'e',(12,5)),
        ( u'(D)igest       本站精华区',("undone",{}),'d' ),
        ( u'(F)avourite    个人收藏夹',("undone",{}),'f' ),
        ( u'(R)ecommend    推荐版面区',("undone",{}),'r' ),
        ( u'(M)ail         处理信笺区',("undone",{}),'m' ),
        ( u'(T)alk         谈天说地区',("undone",{}),'t' ),
        ( u'(I)nfoEdit     个人工具箱',("undone",{}),'i' ),
        ( u'(S)ervice      特别服务区',("undone",{}),'s' ),
        ( u'(C)onfig       系统信息区',("undone",{}),'c' ),
        ( u'(P)ersonal     个人文集区',("undone",{}),'p' ),
        ( u'(G)oodbye    离开逸仙时空',("bye",{}),'g' )),
    "section":(
        # dy + append
          ( u'A) 所有讨论区 -- [ALL]',("boardlist",{}),            'a',(11,41)),
          ( u'N) 阅读新文章',         ("boardlist",{"new":True}),  'n'),
          ( u'E) 回到主选单 -- [EXIT]',("menu",     {"name":"main"}),'e'),
          )
}

default_shortcuts = {
    ascii.k_up:"move_up",
    ascii.k_down:"move_down",
    ascii.k_end:"goto_last",
    ascii.k_home:"goto_first",
    ascii.k_page_up:"page_up",
    ascii.k_page_down:"page_down",
    ascii.k_ctrl_l:"refresh",
    }
