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

import blockdiag.DiagramMetrics
from blockdiag.utils import XY
from blockdiag.utils.collections import namedtuple
import elements


class DiagramMetrics(blockdiag.DiagramMetrics.DiagramMetrics):
    def __init__(self, diagram, **kwargs):
        super(DiagramMetrics, self).__init__(diagram, **kwargs)

        if diagram.page_padding is None:
            if diagram.orientation == 'landscape':
                padding = self.node_width + self.span_width
                self.page_padding = [0, 0, 0, padding]
            else:
                padding = self.node_height + self.span_height
                self.page_padding = [padding, 0, 0, 0]

    def pagesize(self, width=None, height=None):
        if width:
            self.colwidth = width
        else:
            width = self.colwidth

        if height:
            self.colheight = height
        else:
            height = self.colheight

        return super(DiagramMetrics, self).pagesize(width, height)

    def frame(self, lanes):
        dummy = elements.DiagramNode(None)
        dummy.xy = XY(0, 0)
        dummy.colwidth = self.colwidth
        dummy.colheight = self.colheight
        cell = self.cell(dummy, use_padding=False)

        headerbox = (cell.topleft.x - self.span_width / 2,
                     cell.topleft.y - self.node_height - self.span_height - 2,
                     cell.topright.x + self.span_width / 2,
                     cell.topright.y - self.span_height / 2)

        outline = (headerbox[0], headerbox[1], headerbox[2],
                   cell.bottom.y + self.span_height / 2)

        separators = [(XY(headerbox[0], headerbox[3]),
                       XY(headerbox[2], headerbox[3]))]

        for lane in lanes[:-1]:
            x = lane.xy.x + lane.colwidth + 1

            m = self.cell(lane, use_padding=False)
            span_width = self.spreadsheet.span_width[x] / 2
            x1 = m.right.x + span_width

            xy = (XY(x1, outline[1]), XY(x1, outline[3]))
            separators.append(xy)

        Frame = namedtuple('Frame', 'headerbox outline separators')
        return Frame(headerbox, outline, separators)

    def lane_textbox(self, lane):
        headerbox = self.frame([]).headerbox
        m = self.cell(lane, use_padding=False)
        x1 = m.left.x
        x2 = m.right.x

        return (x1, headerbox[1], x2, headerbox[3])
