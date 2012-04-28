# -*- coding: utf-8 -*-
from chaofeng import Frame,launch
from chaofeng.g import marks,mark,static
from chaofeng.ui import Animation

@mark('main')
class Main(Frame):

    def initialize(self):
        self.write(self.background.safe_substitute())
        self.board = Animation(self,self.data)
        self.board.read()
        # self.board.run_bg()
        while True : self.read()

if __name__ == '__main__' :
    from chaofeng import Server
    s = Server(Main)
    s.run()
