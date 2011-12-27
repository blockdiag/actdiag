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

from elements import *
import parser
from blockdiag.utils import XY


class DiagramTreeBuilder:
    def build(self, tree):
        self.diagram = Diagram()
        diagram = self.instantiate(self.diagram, tree)
        for subgroup in diagram.traverse_groups():
            if len(subgroup.nodes) == 0:
                subgroup.group.nodes.remove(subgroup)

        self.bind_edges(diagram)

        if len(self.diagram.lanes) == 0:
            self.diagram.lanes.append(NodeGroup.get(None))

        for node in self.diagram.nodes:
            if node.lane is None:
                edges = DiagramEdge.find(None, node)
                parents = [e.node1 for e in edges if e.node1.lane]
                parents.sort(lambda x, y: cmp(x.order, y.order))

                if parents:
                    node.lane = parents[0].lane
                else:
                    node.lane = self.diagram.lanes[0]

        return diagram

    def belong_to(self, node, lane):
        if lane and node.lane and node.lane != lane:
            print node, node.lane, lane
            msg = "DiagramNode could not belong to two lanes"
            raise RuntimeError(msg)

        node.group = self.diagram
        if lane:
            node.lane = lane

        if node not in self.diagram.nodes:
            self.diagram.nodes.append(node)

    def instantiate(self, group, tree, lane=None):
        for stmt in tree.stmts:
            if isinstance(stmt, parser.Node):
                node = DiagramNode.get(stmt.id)
                node.set_attributes(stmt.attrs)
                self.belong_to(node, lane)

            elif isinstance(stmt, parser.Edge):
                nodes = stmt.nodes.pop(0)
                edge_from = [DiagramNode.get(n) for n in nodes]
                for node in edge_from:
                    self.belong_to(node, lane)

                while len(stmt.nodes):
                    edge_type, edge_to = stmt.nodes.pop(0)
                    edge_to = [DiagramNode.get(n) for n in edge_to]
                    for node in edge_to:
                        self.belong_to(node, lane)

                    for node1 in edge_from:
                        for node2 in edge_to:
                            edge = DiagramEdge.get(node1, node2)
                            if edge_type:
                                attrs = [parser.Attr('dir', edge_type)]
                                edge.set_attributes(attrs)
                            edge.set_attributes(stmt.attrs)

                    edge_from = edge_to

            elif isinstance(stmt, parser.Lane):
                _lane = NodeGroup.get(stmt.id)
                if _lane not in self.diagram.lanes:
                    self.diagram.lanes.append(_lane)

                self.instantiate(group, stmt, _lane)

            elif isinstance(stmt, parser.DefAttrs):
                if lane:
                    lane.set_attributes(stmt.attrs)
                else:
                    self.diagram.set_attributes(stmt.attrs)

            elif isinstance(stmt, parser.AttrClass):
                name = unquote(stmt.name)
                Diagram.classes[name] = stmt

            elif isinstance(stmt, parser.AttrPlugin):
                self.diagram.set_plugin(stmt.name, stmt.attrs)

        group.update_order()
        return group

    def bind_edges(self, group):
        for node in group.nodes:
            if isinstance(node, DiagramNode):
                group.edges += DiagramEdge.find(node)
            else:
                self.bind_edges(node)


class DiagramLayoutManager:
    def __init__(self, diagram):
        self.diagram = diagram

        self.circulars = []
        self.heightRefs = []

    def run(self):
        self.edges = [e for e in DiagramEdge.find_all()]
        self.do_layout()
        self.diagram.fixiate()
        self.fixiate_lanes()

    def fixiate_lanes(self):
        height = 0
        for lane in self.diagram.lanes:
            if self.coordinates[lane]:
                for node in self.diagram.nodes:
                    if node.lane == lane:
                        node.xy = XY(node.xy.x, node.xy.y + height)

                height += max(xy.y for xy in self.coordinates[lane]) + 1

            nodes = [n for n in self.diagram.nodes if n.lane == lane]
            x = min(n.xy.x for n in nodes)
            y = min(n.xy.y for n in nodes)
            lane.xy = XY(x, y)
            lane.colwidth = max(n.xy.x + n.colwidth for n in nodes) - x
            lane.colheight = max(n.xy.y + n.colheight for n in nodes) - y

    def do_layout(self):
        self.detect_circulars()

        self.set_node_width()
        self.adjust_node_order()

        height = 0
        self.initialize_markers()
        for node in self.diagram.traverse_nodes():
            if node.xy.x == 0:
                lane = node.lane
                if self.coordinates[lane]:
                    height = max(xy.y for xy in self.coordinates[lane]) + 1
                else:
                    height = 0
                self.set_node_height(node, height)

    def get_related_nodes(self, node, parent=False, child=False):
        uniq = {}
        for edge in self.edges:
            if edge.folded:
                continue

            if parent and edge.node2 == node:
                uniq[edge.node1] = 1
            elif child and edge.node1 == node:
                uniq[edge.node2] = 1

        related = []
        for uniq_node in uniq.keys():
            if uniq_node == node:
                pass
            else:
                related.append(uniq_node)

        related.sort(lambda x, y: cmp(x.order, y.order))
        return related

    def get_parent_nodes(self, node):
        return self.get_related_nodes(node, parent=True)

    def get_child_nodes(self, node):
        return self.get_related_nodes(node, child=True)

    def detect_circulars(self):
        for node in self.diagram.nodes:
            if not [x for x in self.circulars if node in x]:
                self.detect_circulars_sub(node, [node])

        # remove part of other circular
        for c1 in self.circulars:
            for c2 in self.circulars:
                intersect = set(c1) & set(c2)

                if c1 != c2 and set(c1) == intersect:
                    self.circulars.remove(c1)
                    break

    def detect_circulars_sub(self, node, parents):
        for child in self.get_child_nodes(node):
            if child in parents:
                i = parents.index(child)
                self.circulars.append(parents[i:])
            else:
                self.detect_circulars_sub(child, parents + [child])

    def is_circular_ref(self, node1, node2):
        for circular in self.circulars:
            if node1 in circular and node2 in circular:
                parents = []
                for node in circular:
                    for parent in self.get_parent_nodes(node):
                        if not parent in circular:
                            parents.append(parent)

                parents.sort(lambda x, y: cmp(x.order, y.order))

                for parent in parents:
                    children = self.get_child_nodes(parent)
                    if node1 in children and node2 in children:
                        if circular.index(node1) > circular.index(node2):
                            return True
                    elif node2 in children:
                        return True
                    elif node1 in children:
                        return False
                else:
                    if circular.index(node1) > circular.index(node2):
                        return True

        return False

    def set_node_width(self, depth=0):
        for node in self.diagram.traverse_nodes():
            if node.xy.x != depth:
                continue

            for child in self.get_child_nodes(node):
                if self.is_circular_ref(node, child):
                    pass
                elif node == child:
                    pass
                elif child.xy.x > node.xy.x + node.colwidth:
                    pass
                else:
                    child.xy = XY(node.xy.x + node.colwidth, 0)

        nodes_iter = self.diagram.traverse_nodes()
        depther_node = [x for x in nodes_iter if x.xy.x > depth]
        if len(depther_node) > 0:
            self.set_node_width(depth + 1)

    def adjust_node_order(self):
        for node in self.diagram.traverse_nodes():
            parents = self.get_parent_nodes(node)
            if len(set(parents)) > 1:
                for i in range(1, len(parents)):
                    idx1 = self.diagram.nodes.index(parents[i - 1])
                    idx2 = self.diagram.nodes.index(parents[i])
                    if idx1 < idx2:
                        self.diagram.nodes.remove(parents[i])
                        self.diagram.nodes.insert(idx1 + 1, parents[i])
                    else:
                        self.diagram.nodes.remove(parents[i - 1])
                        self.diagram.nodes.insert(idx2 + 1, parents[i - 1])

            if isinstance(node, NodeGroup):
                nodes = [n for n in node.nodes if n in self.diagram.nodes]
                if nodes:
                    idx = min(self.diagram.nodes.index(n) for n in nodes)
                    if idx < self.diagram.nodes.index(node):
                        self.diagram.nodes.remove(node)
                        self.diagram.nodes.insert(idx + 1, node)

        self.diagram.update_order()

    def initialize_markers(self):
        self.coordinates = {}
        for lane in self.diagram.lanes:
            self.coordinates[lane] = []

    def mark_xy(self, node):
        xy = node.xy
        for w in range(node.colwidth):
            for h in range(node.colheight):
                self.coordinates[node.lane].append(XY(xy.x + w, xy.y + h))

    def is_marked(self, lane, xy):
        return xy in self.coordinates[lane]

    def set_node_height(self, node, height=0):
        xy = XY(node.xy.x, height)
        if self.is_marked(node.lane, xy):
            return False
        node.xy = xy
        self.mark_xy(node)

        count = 0
        children = self.get_child_nodes(node)
        children.sort(lambda x, y: cmp(x.xy.x, y.xy.y))
        for child in children:
            if child.id in self.heightRefs:
                pass
            elif node is not None and node.xy.x >= child.xy.x:
                pass
            else:
                if node.lane == child.lane:
                    h = height
                else:
                    h = 0

                while True:
                    if self.set_node_height(child, h):
                        child.xy = XY(child.xy.x, h)
                        self.mark_xy(child)
                        self.heightRefs.append(child.id)

                        count += 1
                        break
                    elif node.lane != child.lane:
                        h += 1
                    else:
                        if count == 0:
                            return False

                        h += 1

                if node.lane == child.lane:
                    height = h + 1

        return True


class ScreenNodeBuilder:
    @classmethod
    def build(klass, tree, separate=False):
        DiagramNode.clear()
        DiagramEdge.clear()
        NodeGroup.clear()

        diagram = DiagramTreeBuilder().build(tree)
        DiagramLayoutManager(diagram).run()
        diagram.fixiate(True)

        if diagram.orientation == 'portrait':
            klass.rotate_diagram(diagram)

        return diagram

    @classmethod
    def rotate_diagram(klass, diagram):
        for node in diagram.traverse_nodes():
            node.xy = XY(node.xy.y, node.xy.x)
            node.colwidth, node.colheight = (node.colheight, node.colwidth)

        for lane in diagram.lanes:
            lane.xy = XY(lane.xy.y, lane.xy.x)
            lane.colwidth, lane.colheight = (lane.colheight, lane.colwidth)

        size = (diagram.colheight, diagram.colwidth)
        diagram.colwidth, diagram.colheight = size
