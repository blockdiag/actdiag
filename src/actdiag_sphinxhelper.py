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

import actdiag.parser
import actdiag.builder
import actdiag.drawer
core = actdiag

import blockdiag.utils.bootstrap
import blockdiag.utils.collections
import blockdiag.utils.fontmap
utils = blockdiag.utils

from actdiag.utils.rst import nodes
from actdiag.utils.rst import directives

# FIXME: obsoleted interface (keep for compatibility)
(command, parser, builder, drawer, collections,
 FontMap, blockdiag, BlockdiagDirective)
from blockdiag.utils import collections
from blockdiag.utils.fontmap import FontMap
from actdiag import command, parser, builder, drawer
from actdiag.utils.rst.directives import actdiag, ActdiagDirective

(collections, FontMap, command, parser, builder, drawer,
 actdiag, ActdiagDirective)
