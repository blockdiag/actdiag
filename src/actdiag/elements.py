#!bin/py
# -*- coding: utf-8 -*-

import re
import sys
import blockdiag.elements
from blockdiag.elements import *
from blockdiag.utils.XY import XY


class Diagram(blockdiag.elements.Diagram):
    def __init__(self):
        super(Diagram, self).__init__()

        self.orientation = 'portrait'
        self.lanes = []


class NodeGroup(blockdiag.elements.NodeGroup):
    def __init__(self, id):
        super(NodeGroup, self).__init__(id)

        self.color = 'none'
