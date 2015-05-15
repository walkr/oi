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

    def test_add_command_for_program(self):
        self.p.add_command('test', lambda p: 'test')

    def test_add_local_command_for_ctl(self):
        self.ctl.add_command('test', lambda p: 'test')
        dest, res, err = self.ctl.call('test')

        self.assertEqual(dest, 'local')
        self.assertEqual(res, 'test')
        self.assertIsNone(err)
