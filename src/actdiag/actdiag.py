#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
from ConfigParser import SafeConfigParser
from optparse import OptionParser
from elements import *
import DiagramDraw
import diagparser
from blockdiag import noderenderer
from blockdiag.utils.XY import XY
from blockdiag import utils


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
            if isinstance(stmt, diagparser.Node):
                node = DiagramNode.get(stmt.id)
                node.set_attributes(stmt.attrs)
                self.belong_to(node, lane)

            elif isinstance(stmt, diagparser.Edge):
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
                                attrs = [diagparser.Attr('dir', edge_type)]
                                edge.set_attributes(attrs)
                            edge.set_attributes(stmt.attrs)

                    edge_from = edge_to

            elif isinstance(stmt, diagparser.Lane):
                _lane = NodeGroup.get(stmt.id)
                if _lane not in self.diagram.lanes:
                    self.diagram.lanes.append(_lane)

                self.instantiate(group, stmt, _lane)

            elif isinstance(stmt, diagparser.DefAttrs):
                if lane:
                    lane.set_attributes(stmt.attrs)
                else:
                    self.diagram.set_attributes(stmt.attrs)

            else:
                raise AttributeError("Unknown sentense: " + str(type(stmt)))

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

    def do_layout(self):
        self.detect_circulars()

        self.set_node_width()
        self.adjust_node_order()

        height = 0
        toplevel_nodes = [x for x in self.diagram.traverse_nodes() if x.xy.x == 0]
        self.initialize_markers()
        for node in self.diagram.traverse_nodes():
            if node.xy.x == 0:
                lane = node.lane
                if self.coordinates[lane]:
                    height = max(xy.y for xy in self.coordinates[lane]) + 1
                else:
                    height = 0
                self.set_node_height(node, height)

        for node in self.diagram.traverse_nodes():
            node.xy = XY(node.xy.x + 1, node.xy.y)

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
                elif child.xy.x > node.xy.x + node.width:
                    pass
                else:
                    child.xy = XY(node.xy.x + node.width, 0)

        depther_node = [x for x in self.diagram.traverse_nodes() if x.xy.x > depth]
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
        for w in range(node.width):
            for h in range(node.height):
                self.coordinates[node.lane].append(XY(xy.x + w, xy.y + h))

    def is_makred(self, lane, xy):
        return xy in self.coordinates[lane]

    def set_node_height(self, node, height=0):
        xy = XY(node.xy.x, height)
        if self.is_makred(node.lane, xy):
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
            node.width, node.height = (node.height, node.width)

        diagram.width, diagram.height = (diagram.height, diagram.width)


def parse_option():
    usage = "usage: %prog [options] infile"
    p = OptionParser(usage=usage)
    p.add_option('-a', '--antialias', action='store_true',
                 help='Pass diagram image to anti-alias filter')
    p.add_option('-c', '--config',
                 help='read configurations from FILE', metavar='FILE')
    p.add_option('-o', dest='filename',
                 help='write diagram to FILE', metavar='FILE')
    p.add_option('-f', '--font', default=[], action='append',
                 help='use FONT to draw diagram', metavar='FONT')
    p.add_option('-P', '--pdb', dest='pdb', action='store_true', default=False,
                 help='Drop into debugger on exception')
    p.add_option('-s', '--separate', action='store_true',
                 help='Separate diagram images for each group (SVG only)')
    p.add_option('-T', dest='type', default='PNG',
                 help='Output diagram as TYPE format')
    options, args = p.parse_args()

    if len(args) == 0:
        p.print_help()
        sys.exit(0)

    options.type = options.type.upper()
    if not options.type in ('SVG', 'PNG', 'PDF'):
        msg = "ERROR: unknown format: %s\n" % options.type
        sys.stderr.write(msg)
        sys.exit(0)

    if options.type == 'PDF':
        try:
            import reportlab.pdfgen.canvas
        except ImportError:
            msg = "ERROR: colud not output PDF format; Install reportlab\n"
            sys.stderr.write(msg)
            sys.exit(0)

    if options.separate and options.type != 'SVG':
        msg = "ERROR: --separate option work in SVG images.\n"
        sys.stderr.write(msg)
        sys.exit(0)

    if options.config and not os.path.isfile(options.config):
        msg = "ERROR: config file is not found: %s\n" % options.config
        sys.stderr.write(msg)
        sys.exit(0)

    configpath = options.config or "%s/.blockdiagrc" % os.environ.get('HOME')
    if os.path.isfile(configpath):
        config = SafeConfigParser()
        config.read(configpath)

        if config.has_option('blockdiag', 'fontpath'):
            fontpath = config.get('blockdiag', 'fontpath')
            options.font.append(fontpath)

    return options, args


def detectfont(options):
    fonts = options.font + \
            ['c:/windows/fonts/VL-Gothic-Regular.ttf',  # for Windows
             'c:/windows/fonts/msmincho.ttf',  # for Windows
             '/usr/share/fonts/truetype/ipafont/ipagp.ttf',  # for Debian
             '/usr/local/share/font-ipa/ipagp.otf',  # for FreeBSD
             '/System/Library/Fonts/AppleGothic.ttf']  # for MaxOS

    fontpath = None
    for path in fonts:
        if path and os.path.isfile(path):
            fontpath = path
            break

    return fontpath


def main():
    options, args = parse_option()

    infile = args[0]
    if options.filename:
        outfile = options.filename
    else:
        outfile = re.sub('\..*', '', infile) + '.' + options.type.lower()

    if options.pdb:
        sys.excepthook = utils.postmortem

    fontpath = detectfont(options)

    tree = diagparser.parse_file(infile)
    diagram = ScreenNodeBuilder.build(tree, separate=options.separate)
    draw = DiagramDraw.DiagramDraw(options.type, diagram, outfile,
                                   font=fontpath, antialias=options.antialias)
    draw.draw()
    draw.save()


if __name__ == '__main__':
    main()
