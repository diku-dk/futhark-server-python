import unittest
import tempfile
import futhark_server
import futhark_data
import numpy as np

# Sets up and shuts down the server for every test.  This is fine as
# long as doing so is fast, which it certainly is for the non-GPU
# backends, and there is no need to use a GPU backend for these tests.
class Test(unittest.TestCase):
    def setUp(self):
        self.server = futhark_server.Server('./test', '-L')
        self.server.__enter__()

    def tearDown(self):
        self.server.__exit__(None, None, None)

    def test_entry_points(self):
        self.assertIn('f0', self.server.cmd_entry_points())

    def test_f0(self):
        self.server.cmd_call('f0', 'v0')
        with tempfile.NamedTemporaryFile() as f:
            self.server.cmd_store(f.name, 'v0')
            self.assertEqual(f.read(),
                             b'b\x02\x00 i64\x39\x05\x00\x00\x00\x00\x00\x00')

    def test_f0_values(self):
        self.server.cmd_call('f0', 'v0')
        self.assertEqual(self.server.get_value('v0'),
                         np.int64(1337))

    def test_pair_values(self):
        self.server.cmd_call('const_record', 'v0')
        self.assertEqual(self.server.get_value('v0'),
                         (np.int64(42),
                          True))

    def test_pair_bytes(self):
        self.server.cmd_call('const_record', 'v0')
        bs = self.server.get_value_bytes('v0')
        self.assertEqual(type(bs), bytes)
        self.server.put_value_bytes(bs, ('v1', 'r'))
        bs2 = self.server.get_value_bytes('v1')
        self.assertEqual(bs, bs2)

    def test_exception(self):
        with self.assertRaises(futhark_server.Failure):
            self.server.cmd_call('does_not_exist')

if __name__ == '__main__':
    unittest.main()
