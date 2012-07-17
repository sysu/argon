#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')

from model import manager
import traceback

def main():

    for section_num in range(10):

        sid = manager.section.add_section(sectionname='Section[%s]' % section_num,
                                          description=u'我的编号的是 %s ' % section_num)

        for board_num in range(40):
            try:
                raw_input()
                boardname='{%s}Board[%s]' % (sid,board_num)
                manager.board.add_board(sid=sid,
                                        boardname=boardname,
                                        description=u'我是本区第 %s 个讨论区' % board_num)
                manager.post._create_table(boardname)
            except Exception as e:
                traceback.print_exc()                
