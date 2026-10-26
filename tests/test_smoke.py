import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rf433 import __version__  # noqa: E402
from rf433.cli import build_parser, main  # noqa: E402
from rf433.commands import COMMANDS  # noqa: E402


class SmokeTest(unittest.TestCase):
    def test_commands_are_registered(self):
        names = [command.name for command in COMMANDS]
        self.assertEqual(names, ["send", "raw", "list", "check", "info", "clean", "frame", "learn"])

    def test_every_command_parses_its_help(self):
        parser = build_parser([command() for command in COMMANDS])
        for command in COMMANDS:
            with self.subTest(command=command.name), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    parser.parse_args([command.name, "--help"])
                self.assertEqual(raised.exception.code, 0)

    def test_version(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit):
            main(["--version"])
        self.assertIn(__version__, output.getvalue())


if __name__ == "__main__":
    unittest.main()
