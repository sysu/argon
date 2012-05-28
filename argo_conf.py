# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
    argo 的全局配置文件
'''

class ConfigDB:
    '''
        Database config
    '''
    # host= "10.42.43.1"
    host = "localhost"
    port= 3306
    user= "bbs"
    passwd= "forargo"
    dbname = "argo"

class ConfigCache:
    '''
        Cache config
    '''
    # host = '10.42.43.1'
    host = "localhost"
    port = 6379


#class ConfigTelnetServer:
#   pass


#class ConfigWebServer:
#   pass


class ConfigTestDate:
    '''
    Setting of section.
    May be remove.
    '''
    section = (
        ("BBS 系统","[站务] [意见]"),
        ("校园社团","[校园] [社团]"),
        ("院系交流","[院系] [交流]"),
        ("电脑科技","[电脑] [系统]"),
        ("休闲娱乐","[休闲] [娱乐]"),
        ("文化艺术","[文化] [艺术]"),
        ("学术科学","[学术] [科学]"),
        ("谈天说地","[闲聊] [感悟]"),
        ("社会信息","[信息] [招聘]"),
        ("体育健身","[体育] [运动]")
        )

    board = (
        {
            "sid":3,
            "boardname":"Test1",
            "description":"for test1",
            "bm":"111",
            },
        {
            "sid":3,
            "boardname":"Test2",
            "description":"for test2",
            "bm":"222",
            },
        {
            "sid":3,
            "boardname":"Test3",
            "description":"for test3",
            "bm":"333",
            },
        {
            "sid":3,
            "boardname":"Test4",
            "description":"for test4",
            "bm":"444",
            },
        {
            "sid":4,
            "boardname":"Sys",
            "description":"for sys",
            },
        )
