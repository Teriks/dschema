import os
import sys
import unittest

import dschema

script_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(1, os.path.abspath(
    os.path.join(script_dir, os.path.join('..', '..'))))


class NamespaceTest(unittest.TestCase):

    def test_namespace(self):
        ns = dschema.Namespace({'a': 1, 'b': 2, 'c': 'test'})

        self.assertEqual(ns.a, 1)
        self.assertEqual(ns.b, 2)
        self.assertEqual(ns.c, 'test')
