import unittest
import oi


class TestOi(unittest.TestCase):

    def setUp(self):
        address = None
        p = oi.Program('test program', address)
        c = oi.CtlProgram('test program ctl', address)

    def test(self):
        self.assertTrue(True)
