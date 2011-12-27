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

import blockdiag.drawer
from metrics import DiagramMetrics


class DiagramDraw(blockdiag.drawer.DiagramDraw):
    MetricsClass = DiagramMetrics

    def _draw_elements(self, **kwargs):
        m = self.metrics

        # render frame of activity lanes
        frame = m.frame(self.diagram.lanes)
        color = "#ffff99"
        self.drawer.rectangle(frame.headerbox, fill=color, outline=color)
        self.drawer.rectangle(frame.outline, outline='gray')
        for xy in frame.separators:
            self.drawer.line(xy, fill='gray')

        # render label of lanes
        for i, lane in enumerate(self.diagram.lanes):
            if lane.label:
                label = lane.label
            elif isinstance(lane.id, unicode):
                label = lane.id
            else:
                label = u'Lane %d' % (i + 1)

            textbox = m.lane_textbox(lane)
            self.drawer.textarea(textbox, label, fill=self.fill,
                                 font=self.metrics.font_for(lane))

        super(DiagramDraw, self)._draw_elements(**kwargs)
