import unittest

import support  # noqa: F401
from rf433.errors import Rf433Error
from rf433.model import Code, Remote, RemoteCode, check_repeat


class CodeTest(unittest.TestCase):
    def test_parse_accepts_spaces_commas_and_signs(self):
        expected = (300, 900, 300, 9300)
        for text in ("300 900 300 9300", "300,900,300,9300", "+300 -900 +300 -9300", " 300,\n900  300\t9300 "):
            with self.subTest(text=text):
                self.assertEqual(Code.parse(text).values, expected)

    def test_parse_rejects_other_text(self):
        for text in ("300 abc", "300 9.5", "0x12"):
            with self.subTest(text=text), self.assertRaises(Rf433Error):
                Code.parse(text)

    def test_format_duration_and_pause(self):
        code = Code((300, 900, 300, 9300))
        self.assertEqual(code.format(), "300 900 300 9300")
        self.assertEqual(code.duration, 10800)
        self.assertEqual(code.pause, 9300)

    def test_valid_code_has_no_problems(self):
        self.assertEqual(Code(tuple(support.frame("0101"))).problems(), [])

    def test_problems(self):
        cases = {
            (300,): "at least one pulse and one pause",
            (300, 900, 300): "must end with a pause",
            (300, 0, 300, 9300): "zero values",
            (100,) * 1026: "1026 values, at most 1025",
            (400000, 99000, 1100, 9000): "500.1 ms long, at most 500 ms",
        }
        for values, message in cases.items():
            with self.subTest(message=message):
                self.assertIn(message, "; ".join(Code(values).problems()))

    def test_limits_are_inclusive(self):
        self.assertEqual(Code((100,) * 1024).problems(), [])
        self.assertEqual(Code((200000, 100000, 200000, 100000)).problems(), [])

    def test_check_raises_with_all_problems(self):
        with self.assertRaises(Rf433Error) as raised:
            Code((300, 0, 300)).check()
        self.assertIn("zero values", str(raised.exception))
        self.assertIn("end with a pause", str(raised.exception))

    def test_check_repeat(self):
        self.assertEqual(check_repeat(1, 100), 1)
        self.assertEqual(check_repeat(100, 100), 100)
        for value in (0, 101, -1, True, "5", 2.0, None):
            with self.subTest(value=value), self.assertRaises(Rf433Error):
                check_repeat(value, 100)

    def test_repeat_of_prefers_code_then_remote_then_default(self):
        code = RemoteCode("A", Code((300, 9300)))
        remote = Remote("R")
        self.assertEqual(remote.repeat_of(code, 10), 10)
        remote.repeat = 20
        self.assertEqual(remote.repeat_of(code, 10), 20)
        self.assertEqual(remote.repeat_of(None, 10), 20)
        code.repeat = 30
        self.assertEqual(remote.repeat_of(code, 10), 30)


if __name__ == "__main__":
    unittest.main()
