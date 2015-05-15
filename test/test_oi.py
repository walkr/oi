import unittest
import oi


class TestOi(unittest.TestCase):

    def setUp(self):
        self.address = 'ipc:///tmp/test-programd.sock'
        self.p = oi.Program('programd', self.address)
        self.ctl = oi.CtlProgram('programctl', self.address)

    def tearDown(self):
        self.p.service.sock.close()
        self.ctl.client.sock.close()

    # --------------------------------------

    def test_new_program(self):
        self.assertIsNotNone(self.p)

    def test_new_ctl(self):
        self.assertIsNotNone(self.ctl)

    def test_add_command(self):
        self.p.add_command('test', lambda p: 'test')
