# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import static,mark
from chaofeng.ui import TextEditor
from model import manager
from argo_frame import ArgoBaseFrame,in_history

import config

class ArgoEditor(TextEditor):

    key_maps = TextEditor.key_maps.copy()

    def acceptable(self,char):
        return True

@mark('edit_post')
class EditFrame(ArgoBaseFrame):

    x_editor = ArgoEditor()

    def initialize(self,callback,preparation=None):
        self.editor = self.load(self.x_editor,preparation)
        self.callback = callback
        self.refresh()

    def get(self,data):
        self.editor.send(data)
        if data in ac.k_ctrl_x :
            self.callback(dict(title=self.editor.title(),
                               content=self.editor.fetch()))
