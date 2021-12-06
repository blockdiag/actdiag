# -*- coding: utf-8 -*-

# Copyright (c) 2008/2009 Andrey Vlasovskikh
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

r'''A DOT language parser using funcparserlib.

The parser is based on [the DOT grammar][1]. It is pretty complete with a few
not supported things:

* Ports and compass points
* XML identifiers

At the moment, the parser builds only a parse tree, not an abstract syntax tree
(AST) or an API for dealing with DOT.

  [1]: http://www.graphviz.org/doc/info/lang.html
'''

import io
from collections import namedtuple
from re import DOTALL, MULTILINE

from blockdiag.parser import create_mapper, oneplus_to_list
from funcparserlib.lexer import LexerError, Token, make_tokenizer
from funcparserlib.parser import a, finished, many, maybe, skip, some

Diagram = namedtuple('Diagram', 'id stmts')
Lane = namedtuple('Lane', 'id stmts')
Node = namedtuple('Node', 'id attrs')
Attr = namedtuple('Attr', 'name value')
Edge = namedtuple('Edge', 'from_nodes edge_type to_nodes attrs')
Extension = namedtuple('Extension', 'type name attrs')
Statements = namedtuple('Statements', 'stmts')


class ParseException(Exception):
    pass


def tokenize(string):
    """str -> Sequence(Token)"""
    # flake8: NOQA
    specs = [                                                           # NOQA
        ('Comment', (r'/\*(.|[\r\n])*?\*/', MULTILINE)),                # NOQA
        ('Comment', (r'(//|#).*',)),                                    # NOQA
        ('NL',      (r'[\r\n]+',)),                                     # NOQA
        ('Space',   (r'[ \t\r\n]+',)),                                  # NOQA
        ('Name',    ('[A-Za-z_0-9\u0080-\uffff]' +                      # NOQA
                     '[A-Za-z_\\-.0-9\u0080-\uffff]*',)),               # NOQA
        ('Op',      (r'[{};,=\[\]]|(<->)|(<-)|(--)|(->)',)),            # NOQA
        ('Number',  (r'-?(\.[0-9]+)|([0-9]+(\.[0-9]*)?)',)),            # NOQA
        ('String',  (r'(?P<quote>(""")|(\'\'\')|"|\').*?(?<!\\)(?P=quote)', DOTALL)),  # NOQA
    ]
    useless = ['Comment', 'NL', 'Space']
    t = make_tokenizer(specs)
    return [x for x in t(string) if x.type not in useless]


def parse(seq):
    """Sequence(Token) -> object"""
    tokval = lambda x: x.value
    op = lambda s: a(Token('Op', s)) >> tokval
    op_ = lambda s: skip(op(s))
    _id = some(lambda t: t.type in ['Name', 'Number', 'String']) >> tokval
    keyword = lambda s: a(Token('Name', s)) >> tokval

    def make_node_list(node_list, attrs):
        return Statements([Node(node, attrs) for node in node_list])

    def make_edge(first, edge_type, second, followers, attrs):
        edges = [Edge(first, edge_type, second, attrs)]

        from_node = second
        for edge_type, to_node in followers:
            edges.append(Edge(from_node, edge_type, to_node, attrs))
            from_node = to_node

        return Statements(edges)

    #
    # parts of syntax
    #
    node_list = (
        _id +
        many(op_(',') + _id)
        >> create_mapper(oneplus_to_list)
    )
    option_stmt = (
        _id +
        maybe(op_('=') + _id)
        >> create_mapper(Attr)
    )
    option_list = (
        maybe(op_('[') + option_stmt + many(op_(',') + option_stmt) + op_(']'))
        >> create_mapper(oneplus_to_list, default_value=[])
    )

    #  node (node list) statement::
    #     A;
    #     B [attr = value, attr = value];
    #     C, D [attr = value, attr = value];
    #
    node_stmt = (
        node_list + option_list
        >> create_mapper(make_node_list)
    )

    #  edge statement::
    #     A -> B;
    #     A <- B;
    #
    edge_relation = (
        op('->') | op('--') | op('<-') | op('<->')
    )
    edge_stmt = (
        node_list +
        edge_relation +
        node_list +
        many(edge_relation + node_list) +
        option_list
        >> create_mapper(make_edge)
    )

    #  attributes statement::
    #     default_shape = box;
    #     default_fontsize = 16;
    #
    attribute_stmt = (
        _id + op_('=') + _id
        >> create_mapper(Attr)
    )

    #  extension statement (class, plugin)::
    #     class red [color = red];
    #     plugin attributes [name = Name];
    #
    extension_stmt = (
        (keyword('class') | keyword('plugin')) +
        _id +
        option_list
        >> create_mapper(Extension)
    )

    #  lane statement::
    #     lane A [color = red];
    #     lane {
    #        A;
    #     }
    #
    lane_declare_stmt = (
        skip(keyword('lane')) +
        _id +
        option_list
        >> create_mapper(Lane)
    )
    lane_inline_stmt = (
        edge_stmt |
        attribute_stmt |
        node_stmt
    )
    lane_inline_stmt_list = (
        many(lane_inline_stmt + skip(maybe(op(';'))))
    )
    lane_stmt = (
        skip(keyword('lane')) +
        maybe(_id) +
        op_('{') +
        lane_inline_stmt_list +
        op_('}')
        >> create_mapper(Lane)
    )

    #
    # diagram statement::
    #     actdiag {
    #        A;
    #     }
    #
    diagram_id = (
        (keyword('diagram') | keyword('actdiag')) +
        maybe(_id)
        >> list
    )
    diagram_inline_stmt = (
        extension_stmt |
        edge_stmt |
        lane_stmt |
        lane_declare_stmt |
        attribute_stmt |
        node_stmt
    )
    diagram_inline_stmt_list = (
        many(diagram_inline_stmt + skip(maybe(op(';'))))
    )
    diagram = (
        maybe(diagram_id) +
        op_('{') +
        diagram_inline_stmt_list +
        op_('}')
        >> create_mapper(Diagram)
    )
    dotfile = diagram + skip(finished)

    return dotfile.parse(seq)


def sort_tree(tree):
    def weight(node):
        if isinstance(node, (Attr, Extension)):
            return 1
        else:
            return 2

    if hasattr(tree, 'stmts'):
        tree.stmts.sort(key=lambda x: weight(x))
        for stmt in tree.stmts:
            sort_tree(stmt)

    return tree


def parse_string(string):
    try:
        tree = parse(tokenize(string))
        return sort_tree(tree)
    except LexerError as e:
        message = "Got unexpected token at line %d column %d" % e.place
        raise ParseException(message)
    except Exception as e:
        raise ParseException(str(e))


def parse_file(path):
    input = io.open(path, 'r', encoding='utf-8-sig').read()
    return parse_string(input)
