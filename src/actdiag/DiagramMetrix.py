#!bin/py
# -*- coding: utf-8 -*-

import blockdiag.DiagramMetrix
from blockdiag.utils.namedtuple import namedtuple
from blockdiag.utils.XY import XY


class DiagramMetrix(blockdiag.DiagramMetrix.DiagramMetrix):
    def __init__(self, diagram, **kwargs):
        super(DiagramMetrix, self).__init__(diagram, **kwargs)

        if diagram.page_padding is None:
            if diagram.orientation == 'landscape':
                padding = self.nodeWidth + self.spanWidth
                self['pagePadding'] = [0, 0, 0, padding]
            else:
                padding = self.nodeHeight + self.spanHeight
                self['pagePadding'] = [padding, 0, 0, 0]

    def originalMetrix(self):
        kwargs = {}
        for key in self:
            kwargs[key] = self[key]
        kwargs['scale_ratio'] = 1

        return DiagramMetrix(self, **kwargs)

    def pageSize(self, width=None, height=None):
        if width:
            DiagramMetrix._width = width
        else:
            width = DiagramMetrix._width

        if height:
            DiagramMetrix._height = height
        else:
            height = DiagramMetrix._height

        return super(DiagramMetrix, self).pageSize(width, height)

    def frame(self, lanes):
        pagesize = self.pageSize()
        margin = self.pageMargin

        headerbox = (margin.x - self.spanWidth / 2,
                     margin.y - self.cellSize * 2,
                     pagesize.x - margin.x + self.spanWidth / 2,
                     margin.y - self.cellSize + self.nodeHeight + \
                     self.spanHeight / 2)

        outline = (headerbox[0], headerbox[1], headerbox[2],
                   pagesize.y - margin.y + self.cellSize * 2)

        separators = [(XY(headerbox[0], headerbox[3]),
                       XY(headerbox[2], headerbox[3]))]

        for lane in lanes[:-1]:
            sep = lane.xy.x + lane.width
            x1 = headerbox[0] + sep * (self.nodeWidth + self.spanWidth)

            xy = (XY(x1, outline[1]), XY(x1, outline[3]))
            separators.append(xy)

        Frame = namedtuple('Frame', 'headerbox outline separators')
        return Frame(headerbox, outline, separators)

    def lane_textbox(self, lane):
        headerbox = self.frame([]).headerbox
        x1 = headerbox[0] + lane.xy.x * (self.nodeWidth + self.spanWidth)
        x2 = x1 + lane.width * (self.nodeWidth + self.spanWidth)

        return (x1, headerbox[1], x2, headerbox[3])
