#!bin/py
# -*- coding: utf-8 -*-

import blockdiag.DiagramDraw
from blockdiag.utils.XY import XY


class DiagramDraw(blockdiag.DiagramDraw.DiagramDraw):
    def _draw_background(self):
        super(DiagramDraw, self)._draw_background()
        self.draw_lane()

    def draw_lane(self):
        m = self.metrix
        pagesize = self.pagesize()
        margin = m.pageMargin

        # draw background of lane-header
        headerbox = (margin.x - m.spanWidth / 2,
                     margin.y - m.cellSize,
                     pagesize.x - margin.x + m.spanWidth / 2,
                     margin.y - m.cellSize + m.nodeHeight + m.spanHeight / 2)
        self.drawer.rectangle(headerbox, fill='#ffff99', outline='#ffff99')

        # draw frame of lane
        lane_frame = (headerbox[0], headerbox[1], headerbox[2],
                      pagesize.y - m.cellSize)
        self.drawer.rectangle(lane_frame, outline=self.fill)

        # draw bottom line of lane-header
        xy = (XY(headerbox[0], headerbox[3]), XY(headerbox[2], headerbox[3]))
        self.drawer.line(xy, fill=self.fill)

        lanewidth = m.nodeWidth + m.spanWidth

        for i in range(self.diagram.width):
            x1 = headerbox[0] + i * (m.nodeWidth + m.spanWidth)
            x2 = x1 + m.nodeWidth + m.spanWidth

            # draw lane splitter
            if x2 + 1 != headerbox[2]:
                xy = (XY(x2, lane_frame[1]), XY(x2, lane_frame[3]))
                self.drawer.line(xy, fill=self.fill)

            # draw lane-label
            label = 'Lane %d' % (i + 1)
            textbox = (x1, headerbox[1], x2, headerbox[3])
            self.drawer.textarea(textbox, label, fill=self.fill,
                                 font=self.font, fontsize=self.metrix.fontSize)
