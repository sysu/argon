from chaofeng import static
from chaofeng.g import mark
from chaofeng.ui import Animation
from chaofeng import ascii as ac
from argo_frame import ArgoBaseFrame,ArgoKeymapsFrame

@mark('tutorial')
class TutorialFrame(ArgoKeymapsFrame):

    x_anim = Animation()
    key_maps = {
        ac.k_ctrl_c : "goto_back"
        }
    
    def initialize(self,tutorial):
        self.anim = self.load(self.x_anim,static[tutorial],
                              auto_play=True,playone=True)

    def get(self,data):
        self.anim.send(data)
        super(TutorialFrame,self).get(data)

    def play_done(self):
        self.goto_back()
