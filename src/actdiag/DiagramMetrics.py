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
from blockdiag.utils.namedtuple import namedtuple
from blockdiag.utils.XY import XY


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
            DiagramMetrics._width = width
        else:
            width = DiagramMetrics._width

        if height:
            DiagramMetrics._height = height
        else:
            height = DiagramMetrics._height

        return super(DiagramMetrics, self).pagesize(width, height)

    def frame(self, lanes):
        pagesize = self.pagesize()
        margin = self.page_margin

        headerbox = (margin.x - self.span_width / 2,
                     margin.y - self.cellsize * 2,
                     pagesize.x - margin.x + self.span_width / 2,
                     margin.y - self.cellsize + self.node_height + \
                     self.span_height / 2)

        outline = (headerbox[0], headerbox[1], headerbox[2],
                   pagesize.y - margin.y + self.cellsize * 2)

        separators = [(XY(headerbox[0], headerbox[3]),
                       XY(headerbox[2], headerbox[3]))]

        for lane in lanes[:-1]:
            sep = lane.xy.x + lane.colwidth
            x1 = headerbox[0] + sep * (self.node_width + self.span_width)

            xy = (XY(x1, outline[1]), XY(x1, outline[3]))
            separators.append(xy)

        Frame = namedtuple('Frame', 'headerbox outline separators')
        return Frame(headerbox, outline, separators)

    def lane_textbox(self, lane):
        headerbox = self.frame([]).headerbox
        x1 = headerbox[0] + lane.xy.x * (self.node_width + self.span_width)
        x2 = x1 + lane.colwidth * (self.node_width + self.span_width)

        return (x1, headerbox[1], x2, headerbox[3])
