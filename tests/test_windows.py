import unittest

import support
from rf433.errors import Rf433Error
from rf433.model import Code
from rf433.transmit.windows import describe, frames_per_window, plan_windows


class WindowsTest(unittest.TestCase):
    def test_duration_limit(self):
        # two frames of 300 ms minus the last pause of 100 ms are exactly 500 ms
        self.assertEqual(frames_per_window(Code((200000, 100000))), 2)
        self.assertEqual(frames_per_window(Code((200001, 100000))), 1)

    def test_buffer_limit(self):
        # two frames of 512 values minus the last pause are exactly 1023 values
        self.assertEqual(frames_per_window(Code((10,) * 512)), 2)
        self.assertEqual(frames_per_window(Code((10,) * 514)), 1)
        self.assertEqual(frames_per_window(Code((10,) * 1024)), 1)

    def test_plan_fills_windows(self):
        code = Code(tuple(support.frame("0101")))       # 4 bits + sync = 10 values, 14.4 ms
        self.assertEqual(frames_per_window(code), 35)
        self.assertEqual(plan_windows(code, 10), [10])
        self.assertEqual(plan_windows(code, 35), [35])
        self.assertEqual(plan_windows(code, 100), [35, 35, 30])

    def test_code_too_long_for_one_write(self):
        with self.assertRaisesRegex(Rf433Error, "fit into one write"):
            plan_windows(Code((10,) * 1026), 1)

    def test_describe(self):
        code = Code(tuple(support.frame("0101")))
        self.assertEqual(describe(code, 1), "14.4 ms x 1 = 1 window (1)")
        self.assertEqual(describe(code, 100), "14.4 ms x 100 = 3 windows (35+35+30)")


if __name__ == "__main__":
    unittest.main()
