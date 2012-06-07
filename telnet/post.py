from chaofeng import static
from chaofeng.g import mark
from chaofeng.ui import Animation,LongTextBox
from chaofeng import ascii as ac
from argo_frame import ArgoFrame
from model import manager
from texteditor import TextEditor

@mark('help')
class TutorialFrame(ArgoFrame):

    x_anim = Animation()
    key_maps = {
        ac.k_ctrl_c : "goto_back"
        }
    
    def initialize(self,page):
        self.cls()
        self.write(ac.move2(24,40))
        self.anim = self.load(self.x_anim,static['help/'+page],
                              auto_play=True,playone=True)

    def get(self,data):
        self.anim.send(data)
        super(TutorialFrame,self).get(data)

    def play_done(self):
        self.pause()
        self.goto_back()

class ArgoTextBox(ArgoFrame):

    _textbox = LongTextBox()
    key_maps = {
        "Q":"goto_back",
        ac.k_left:"goto_back",
        }
    
    textbox_cmd = {
        ac.k_up : "move_up",
        "k":"move_up",
        ac.k_down : "move_down",
        "j":"move_down",
        ac.k_ctrl_b:"page_up",
        ac.k_page_up:"page_up",
        ac.k_ctrl_f:"page_down",
        ac.k_page_down:"page_down",
        ac.k_right:"page_down",
        ac.k_home:"go_first",
        ac.k_end:"go_last",
        "$":"go_last",
        }
    
    def initialize(self):
        super(ArgoTextBox,self).initialize()
        self.textbox_ = self.load(self._textbox)
        self.textbox_.bind(self.bottom_bar,self.finish)

    def set_text(self,text):
        self.textbox_.set_text(text)
        self.textbox_.display()

    def get(self,data):
        if data in self.textbox_cmd:
            getattr(self.textbox_,self.textbox_cmd[data])()
        self.try_action(data)

@mark('read_post')
class ArgoReadPostFrame(ArgoTextBox):

    def initialize(self,boardname,pid):
        super(ArgoReadPostFrame,self).initialize()
        self.set_post(boardname,pid)

    def get_post(self,boardname,pid):
        return manager.post.get_post(boardname,pid)

    def wrapper_post(self,post):
        return static['post'].safe_substitute(post)

    def set_post(self,boardname,pid):
        if pid is not None:
            self.boardname,self.pid = boardname,pid
            self.post = self.get_post(boardname,pid)
            self.text = self.wrapper_post(self.post)
            self.cls()
            self.set_text(self.text)

    def next_post(self):
        return self.boardname,manager.post.next_post_pid(self.boardname,self.pid)

    def prev_post(self):
        return self.boardname,manager.post.prev_post_pid(self.boardname,self.pid)

    def finish(self,args=None):
        if args is True:
            self.set_post(*self.next_post())
        if args is False:
            self.set_post(*self.prev_post())
        if args is None:
            self.goto_back()

    def bottom_bar(self,fixed=True):
        super(ArgoReadPostFrame,self).bottom_bar(repos=True)

