# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from chaofeng import ascii as ac
from chaofeng.g import static,mark
from chaofeng.ui import TextEditor
from model import manager
from argo_frame import ArgoFrame

import config

class ArgoEditor(TextEditor):

    key_maps = TextEditor.key_maps.copy()

    def acceptable(self,char):
        return True

