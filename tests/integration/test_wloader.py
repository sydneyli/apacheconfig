#
# This file is part of apacheconfig software.
#
# Copyright (c) 2018-2019, Ilya Etingof <etingof@gmail.com>
# License: https://github.com/etingof/apacheconfig/LICENSE.rst
#
import sys
import os

from apacheconfig import *

try:
    import unittest2 as unittest

except ImportError:
    import unittest

class WLoaderApacheConfigsTestCase(unittest.TestCase):
    def testParseFiles(self):
        samples_dir = os.path.join(
            os.path.dirname(__file__),
            'samples', 'perl-config-general'
        )
        for filename in os.listdir(samples_dir):
            filepath = os.path.join(samples_dir, filename)
            if os.path.isdir(filepath):
                continue
            contents = ""
            with open(filepath) as f:
                contents = f.read()
            if "<<EOF" in contents or "/*" in contents:
                # Skip tests files with non-apache constructs for the time being.
                continue
            node = parse_contents(contents)
            self.assertEqual(str(node), contents)

suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
