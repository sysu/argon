import chaofeng.ascii as ac
from chaofeng.ui import TextEditor
from libtelnet import is_chchar
from datetime import datetime

class ArgoEditor(TextEditor):

    key_maps = TextEditor.key_maps
    state_bar_format = ac.save + ac.move2(24,0) + '[1;44;33m%-80s[m' + ac.restore
    
    def init(self,text=''):
        super(ArgoEditor,self).init(text)

    def refresh(self):
        super(ArgoEditor,self).refresh()
        self.state_bar()

    def state_bar(self):
        self.write(self.state_bar_format % datetime.now().ctime())

    def acceptable(self,data):
        return is_chchar(data) or data in ac.printable

    def message(self,text):
        self.frame.write(ac.move2(24,0)+text)
