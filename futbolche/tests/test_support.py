import os
import sys
import unittest


SRC_ROOT = os.path.join(os.path.dirname(__file__), '..', 'src')


class BasePatchedTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if SRC_ROOT not in sys.path:
            sys.path.insert(0, SRC_ROOT)
