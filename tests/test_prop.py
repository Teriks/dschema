import os
import sys
import unittest

import dschema

script_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(1, os.path.abspath(
    os.path.join(script_dir, os.path.join('..', '..'))))


class PropTest(unittest.TestCase):

    def test_prop(self):
        d = dschema.prop(default=2, dict=True, type=int, required=True)

        self.assertDictEqual(d, {'@default': 2, "@dict": True, "@type": int, "@required": True})

        with self.assertRaises(ValueError):
            dschema.prop(unknown_arg='BAD')
