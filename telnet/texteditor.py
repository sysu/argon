# from baseui import BaseUI
import chaofeng.ascii as ac

class BaseUI:pass

class TextEditor(BaseUI):

    key_maps = {
        '\n':"new_line",
        '\r\n':"new_line",
        "\r\x00":"new_line",
        ac.k_del:"backspace",
        ac.k_backspace:"backspace",
        ac.k_ctrl_l:"refresh",
        }
        

    def __init__(self,limit=23,buf_size=32767):
        self.limit = limit
        self.buf_size = buf_size

    def init(self,text=''):
        self.buf = [list(x) for x in text.split('\r\n')]
        self.now = self.buf[len(self.buf)-1]
        
    def fetch(self):
        return '\r\n'.join( ''.join(g) for g in ( ''.join(g) for g in self.buf ))

    def send(self,data):
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()
        data = self.frame.u(data)
        # todo : max_buf_size
        if self.acceptable(data) :
            self.insert(data)

    def write(self,data):
        self.frame.write(data)

    def new_line(self):
        self.now = []
        self.buf.append(self.now)
        self.write('\r\n')

    def backspace(self):
        if self.now :
            self.now.pop()
            self.write(ac.backspace)
        elif len(self.buf)>1 :
            self.buf.pop()
            self.now = self.buf[len(self.buf)-1]
            self.write(ac.movey_p)
            if len(self.now) : self.write(ac.movex(len(self.now)))
    
    def refresh(self):
        self.write(ac.clear)
        self.write(self.fetch())

    def insert(self,char):
        self.now.append(char)
        self.write(char)

    def acceptable(self,char):
        try:
            return char.isalnum()
        except:
            return False
