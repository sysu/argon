#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from model import manager
import traceback

def main(data):

    for section in data:
        attr,boards = section
        try:
            sid = manager.section.add_section(sectionname=attr[0],
                                              description=attr[1])
            print sid
        except Exception,e:
            print e
        sid = raw_input() or sid
        for boardattr in boards:
            try:
                manager.board.add_board(sid=sid,
                                        boardname=boardattr[0],
                                        description=boardattr[1])
                manager.post._create_table(boardattr[0])
            except Exception as e:
                traceback.print_exc()                

if __name__ == '__main__' :

    data = [
        [
            ["BBS 系统","[站务][意见]"],
            [
                ["Test","系统测试"],
                ["BBS_HELP","BBS使用求助"],
                ["Suggest","系统管理大家谈"],
                ["BugReport","系统错误报告"],
                ["notepad","酸甜苦辣留言板"],
                ],
            ],
        [
            ["休闲娱乐","[休闲][娱乐]"],
            [
                ["Joke","每日笑一笑"],
                ],
            ],
        [
            ["谈天说地","[闲聊][感悟]"],
            [
                ["water","你一瓢来我一瓢"],
                ],
            ],
        ]
    
    main(data)
    print 'Done'
