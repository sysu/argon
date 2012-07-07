from chaofeng import Frame, Server
import chaofeng.ascii as c

class Hello(Frame):

    def initialize(self):
        self.write('Hello,World!\r\n')
        self.pause()
        self.close()

if __name__ == '__main__' :
    s = Server(Hello)
    s.run()
