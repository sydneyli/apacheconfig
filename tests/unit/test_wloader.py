#
# This file is part of apacheconfig software.
#
# Copyright (c) 2018-2019, Ilya Etingof <etingof@gmail.com>
# License: https://github.com/etingof/apacheconfig/LICENSE.rst
#
import os
import sys

from apacheconfig import *

try:
    import unittest2 as unittest

except ImportError:
    import unittest

try:
    from unittest import mock

except ImportError:

    import mock

class WLoaderTestCase(unittest.TestCase):

    def _test_item_cases(self, cases, expected_type, options={}):
        for raw, expected in cases:
            node = parse_item(raw, options)
            self.assertEqual(expected, node.value,
                "Expected node('%s').value to be %s, got %s" %
                    (repr(raw), expected, node.value))
            self.assertEqual(raw, str(node),
                "Expected str(node('%s')) to be the same, but got '%s'" %
                    (repr(raw), str(node)))
            self.assertEqual(expected_type, node.type,
                "Expected node('%s').type to be '%s', but got '%s'" %
                    (repr(raw), expected_type, str(node.type)))

    def testLoadStatement(self):
        cases = [
            ('option value', ('option', ' ', 'value')),
            ('  option value', ('  ', 'option', ' ', 'value')),
            ('\noption value', ('\n', 'option', ' ', 'value')),
            ('option "dblquoted value"', ('option', ' ', 'dblquoted value')),
            ("option 'sglquoted value'", ("option", " ", "sglquoted value")),
        ]
        self._test_item_cases(cases, 'statement')

    def testLoadComment(self):
        comment = '# here is a silly comment'
        cases = [
            (comment, (comment,)),
            ('\n' + comment, ('\n', comment)),
            (' ' + comment, (' ', comment)),
        ]
        self._test_item_cases(cases, 'comment')

    def testLoadApacheInclude(self):
        cases = [
            ('include path', ('include', ' ', 'path')),
            ('  include path', ('  ', 'include', ' ', 'path')),
            ('\ninclude path', ('\n', 'include', ' ', 'path')),
        ]
        self._test_item_cases(cases, 'include',
            options={'useapacheinclude': True})

    def testContents(self):
        cases = [
            ('a b\nc d', ('a b', '\nc d')),
            ('  \n', ('  \n',)),
            ('a b  \n', ('a b', '  \n')),
            ('a b # comment', ('a b', ' # comment')),
            ('a b\n<b/>  \n', ('a b', '\n<b/>', '  \n')),
        ]
        for raw, expected in cases:
            node = parse_contents(raw)
            self.assertEqual(len(node), len(expected))
            for got, expected in zip(node, expected):
                self.assertEqual(str(got), expected)
            self.assertEqual(raw, str(node))

    def testBlockCases(self):
        cases = [
            '<b>\nhello there\nit me\n</b>',
            '<b/>',
            '<b name/>',
            '<b>\n</b>',
            '<b  name>\n</b name>',
            '<b>\n</b>',
        ]
        for raw in cases:
            node = parse_block(raw)
            self.assertEqual(raw, str(node))

    def testLoadWholeConfig(self):
        text = """\

# a
a = b

<a block>
  a = b
</a>
a b
<a a block>
c "d d"
</a>
# a
"""
        node = parse_contents(text)
        self.assertEqual(text, str(node))
