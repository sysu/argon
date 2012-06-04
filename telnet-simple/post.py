from chaofeng import static
from chaofeng.g import mark
from chaofeng.ui import Animation
from chaofeng import ascii as ac
from argo_frame import ArgoBaseFrame,ArgoKeymapsFrame

@mark('help')
class TutorialFrame(ArgoKeymapsFrame):

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
