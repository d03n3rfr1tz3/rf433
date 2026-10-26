import os
import shutil
import tempfile
import unittest

import support  # noqa: F401
from rf433.errors import Rf433Error
from rf433.options import Options


class OptionsTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.directory)

    def write(self, text):
        path = os.path.join(self.directory, "options.conf")
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
        return path

    def test_file_values_and_command_line(self):
        path = self.write("[rf433]\ndevice = /dev/lirc-433\nrepeat = 20\ncpu_core = 3\n"
                          "[learn]\ndevice = :STICK\nservice = rtl.service\nseconds = 5\n")
        options = Options.load(path, codes="/tmp/codes")
        self.assertEqual((options.device, options.codes, options.repeat, options.cpu_core, options.priority),
                         ("/dev/lirc-433", "/tmp/codes", 20, 3, 50))
        self.assertEqual((options.learn.device, options.learn.service, options.learn.seconds, options.learn.frequency),
                         (":STICK", "rtl.service", 5, "433.92M"))
        self.assertEqual(Options.load(path, device="/dev/lirc9").device, "/dev/lirc9")

    def test_empty_values_keep_the_default(self):
        options = Options.load(self.write("[rf433]\ndevice =\ncpu_core =\n[learn]\nservice =\n"))
        self.assertEqual((options.device, options.cpu_core, options.learn.service), ("/dev/lirc0", None, ""))

    def test_errors(self):
        cases = {
            "[rf433]\nrepeat = 0\n": "repeat must be a number from 1 to 100",
            "[rf433]\nmax_repeat = 5\nrepeat = 10\n": "repeat must be a number from 1 to 5",
            "[rf433]\npriority = high\n": "priority must be a number from 1 to 99",
            "[rf433]\nspeed = 1\n": "unknown option speed",
            "[sender]\n": "unknown section [sender]",
            "device = x\n": "",
        }
        for text, message in cases.items():
            with self.subTest(text=text), self.assertRaisesRegex(Rf433Error, message.replace("[", r"\[")):
                Options.load(self.write(text))

    def test_missing_file_given_explicitly(self):
        with self.assertRaises(OSError):
            Options.load(os.path.join(self.directory, "missing.conf"))


if __name__ == "__main__":
    unittest.main()
