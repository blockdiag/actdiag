# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import blockdiag.elements
from blockdiag.elements import *


class DiagramNode(blockdiag.elements.DiagramNode):
    lane = None


class NodeGroup(blockdiag.elements.NodeGroup):
    def __init__(self, id):
        super(NodeGroup, self).__init__(id)

        self.color = '#ffff99'


class Diagram(blockdiag.elements.Diagram):
    _DiagramNode = DiagramNode
    _NodeGroup = NodeGroup

    def __init__(self):
        super(Diagram, self).__init__()

        self.orientation = 'portrait'
        self.lanes = []
