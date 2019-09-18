#
# This file is part of apacheconfig software.
#
# Copyright (c) 2018-2019, Ilya Etingof <etingof@gmail.com>
# License: https://github.com/etingof/apacheconfig/LICENSE.rst
#


from apacheconfig import error
from apacheconfig import make_parser
from apacheconfig import make_lexer

import abc, six

def _restore_original(word):
    if getattr(word, 'is_single_quoted', False):
        return "'%s'" % word
    if getattr(word, 'is_double_quoted', False):
        return '"%s"' % word
    return word


@six.add_metaclass(abc.ABCMeta)
class Node():
    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError()

    @property
    def type(self):
        if self._type is None:
            raise NotImplementedError()
        return self._type

class ContentsNode(Node):
    def __init__(self, raw):
        self._contents = []
        for elem in raw[1:]:
            if isinstance(elem, str) and elem.isspace():
                self._contents.append(elem)
            elif elem[0] == "block":
                self._contents.append(BlockNode(elem))
            else:
                self._contents.append(ItemNode(elem))

    def add(index, node):
        pass

    def remove(index):
        pass

    def __len__(self):
        return len(self._contents)

    def __iter__(self):
        return iter(self._contents)

    def __str__(self):
        return "".join([str(item) for item in self._contents])

class ItemNode(Node):
    def __init__(self, raw):
        self._type = raw[0]
        self._value = tuple(raw[1:])

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self):
        return "".join([_restore_original(word) for word in self._value])

class BlockNode(ContentsNode):
    def __init__(self, raw):
        self._whitespace = ""
        start = 1
        if isinstance(raw[start], str) and raw[start].isspace():
            self._whitespace = raw[start]
            start += 1
        self._name = raw[start]
        self._close_name = raw[-1]
        self._empty = len(raw[start + 1]) == 0
        if not self._empty:
            self._contents = ContentsNode(raw[start + 1])

    @property
    def name(self):
        return self._name

    def __str__(self):
        if self._empty:
            return "%s<%s/>" % (self._whitespace, self.name)
        return "%s<%s>%s</%s>" % (self._whitespace, self.name,
                                  str(self._contents), self._close_name)


def _create_parser(options={}, start='contents'):
    options['preserve_whitespace'] = True
    ApacheConfigLexer = make_lexer(**options)
    ApacheConfigParser = make_parser(**options)
    return ApacheConfigParser(ApacheConfigLexer(), start=start)


def parse_contents(raw_str, options={}):
    parser = _create_parser(options, start='contents')
    return ContentsNode(parser.parse(raw_str))


def parse_item(raw_str, options={}):
    parser = _create_parser(options, start='startitem')
    ast = parser.parse(raw_str)
    return ItemNode(parser.parse(raw_str))


def parse_block(raw_str, options={}):
    parser = _create_parser(options, start='block')
    return BlockNode(parser.parse(raw_str))
