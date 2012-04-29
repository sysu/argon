# -*- coding: utf-8 -*-

def get_boardlist_q(sid):
    return [
        {
            "boardname":u"Selection",
            "flag":False,
            "bid":0,
            "total":635,
            "descript":u"选举事务",
            "bm":u"jmf",
            "type":u"本站",
            "online":5,
            },
        ] * 50

def get_board_info(bid):
    '''
    返回bid为bid的讨论区的信息。
    '''
    return {
        "sid":0,
        "boardname":"z",
        }
