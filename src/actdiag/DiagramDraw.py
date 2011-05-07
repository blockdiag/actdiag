#!bin/py
# -*- coding: utf-8 -*-

import blockdiag.DiagramDraw
from blockdiag.utils.XY import XY


class DiagramDraw(blockdiag.DiagramDraw.DiagramDraw):
    def _draw_background(self):
        super(DiagramDraw, self)._draw_background()
        self.draw_lane()

    def draw_lane(self):
        m = self.metrix.originalMetrix()
        pagesize = self.pagesize()
        margin = m.pageMargin

        # render frame of activity lanes
        frame = m.frame(self.diagram.lanes)
        color = "#ffff99"
        self.drawer.rectangle(frame.headerbox, fill=color, outline=color)
        self.drawer.rectangle(frame.outline, outline='gray')
        for xy in frame.separators:
            self.drawer.line(xy, fill='gray')

        # render label of lanes
        for lane in self.diagram.lanes:
            if lane.label:
                label = lane.label
            elif isinstance(lane.id, unicode):
                label = lane.id
            else:
                label = u'Lane %d' % (i + 1)

            textbox = m.lane_textbox(lane)
            self.drawer.textarea(textbox, label, fill=self.fill,
                                 font=self.font, fontsize=self.metrix.fontSize)


from DiagramMetrix import DiagramMetrix
DiagramDraw.set_metrix_class(DiagramMetrix)
