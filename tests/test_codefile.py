import os
import shutil
import tempfile
import textwrap
import unittest

import support
from rf433.codefile import CodeLibrary, format_code, format_remote, parse_text
from rf433.errors import Rf433Error
from rf433.model import Code, Remote, RemoteCode

ON = support.frame("010110")
OFF = support.frame("010101")


def parse(text, max_repeat=100):
    return parse_text(textwrap.dedent(text), "/codes/test.conf", max_repeat)


class ParserTest(unittest.TestCase):
    def test_valid_file(self):
        remotes, problems = parse("""\
            # comment before
            begin remote
              name    Garden
              repeat  15

              begin raw_codes
                # comments and empty lines are allowed anywhere
                name Light_on
                  %s

                name Light_off
                  repeat 30
                  %s
                  %s
              end raw_codes
            end remote
            """ % (" ".join(map(str, ON)), " ".join(map(str, OFF[:8])), " ".join(map(str, OFF[8:]))))
        self.assertEqual(problems, [])
        self.assertEqual(len(remotes), 1)
        remote = remotes[0]
        self.assertEqual((remote.name, remote.repeat, remote.line, remote.file), ("Garden", 15, 2, "test.conf"))
        self.assertEqual(list(remote.codes), ["Light_on", "Light_off"])
        self.assertEqual(remote.codes["Light_on"], RemoteCode("Light_on", Code(tuple(ON)), None, 8))
        self.assertEqual(remote.codes["Light_off"], RemoteCode("Light_off", Code(tuple(OFF)), 30, 11))

    def test_several_remotes_and_signed_values(self):
        remotes, problems = parse("""\
            begin remote
              name One
              begin raw_codes
                name A
                  +300 -9300
              end raw_codes
            end remote
            begin remote
              name Two
              begin raw_codes
                name A
                  300,9300
              end raw_codes
            end remote
            """)
        self.assertEqual(problems, [])
        self.assertEqual([remote.name for remote in remotes], ["One", "Two"])
        self.assertEqual(remotes[0].codes["A"].code, remotes[1].codes["A"].code)

    def assertProblems(self, text, expected, max_repeat=100):
        remotes, problems = parse(text, max_repeat)
        self.assertEqual(len(problems), len(expected), [str(problem) for problem in problems])
        for problem, (where, message) in zip(problems, expected):
            self.assertEqual(problem.where, where)
            self.assertIn(message, problem.message)
        return remotes

    def test_problems_with_line_numbers(self):
        remotes = self.assertProblems("""\
            begin remote
              name Box
              colour red
              begin raw_codes
                name Good
                  300 9300
                name Bad value
                  300 9300
                name Odd
                  300 900 300
                name Zero
                  300 0
                name Good
                  400 9300
                name Empty
                name Late
                  300 9300
                  repeat 5
                volume 3
              end raw_codes
            end remote
            """, [
            ("test.conf:3", "unknown keyword 'colour' in remote"),
            ("test.conf:7", "name must be one word"),
            ("test.conf:10", "Box Odd: code must end with a pause"),
            ("test.conf:12", "Box Zero: code contains zero values"),
            ("test.conf:13", "Box Good is already defined in line 5"),
            ("test.conf:15", "Box Empty: values are missing"),
            ("test.conf:18", "'repeat' belongs directly below the name"),
            ("test.conf:19", "unknown keyword 'volume' in raw_codes"),
        ])
        self.assertEqual(list(remotes[0].codes), ["Good", "Late"])
        self.assertEqual(remotes[0].codes["Good"].code.values, (300, 9300))

    def test_invalid_repeat(self):
        remotes = self.assertProblems("""\
            begin remote
              name Box
              repeat 51
              begin raw_codes
                name A
                  repeat 0
                  300 9300
                name B
                  repeat many
                  300 9300
                name C
                  repeat 50
                  300 9300
              end raw_codes
            end remote
            """, [
            ("test.conf:3", "repeat must be a number from 1 to 50, got 51"),
            ("test.conf:6", "repeat must be a number from 1 to 50, got 0"),
            ("test.conf:9", "got 'many'"),
        ], max_repeat=50)
        remote = remotes[0]
        self.assertIsNone(remote.repeat)
        self.assertEqual(list(remote.codes), ["C"])
        self.assertEqual(remote.codes["C"].repeat, 50)

    def test_structure_problems(self):
        remotes = self.assertProblems("""\
            name Outside
            begin remote
              begin raw_codes
                300 9300
                name A
                  300 9300
              end raw_codes
            end remote
            begin remote
              name Second
              name Again
              begin raw_codes
              end raw_codes
            end remote
            begin remote
              name Open
              begin raw_codes
                name A
                  300 9300
            """, [
            ("test.conf:1", "expected 'begin remote'"),
            ("test.conf:4", "values without 'name' before"),
            ("test.conf:2", "remote without name"),
            ("test.conf:11", "remote Second has a second name Again"),
            ("test.conf:9", "remote Second has no codes"),
            ("test.conf:19", "'end raw_codes' is missing"),
            ("test.conf:19", "'end remote' is missing"),
        ])
        self.assertEqual([remote.name for remote in remotes], ["Open"])
        self.assertEqual(list(remotes[0].codes), ["A"])

    def test_missing_end_before_next_remote(self):
        remotes = self.assertProblems("""\
            begin remote
              name One
              begin raw_codes
                name A
                  300 9300
            begin remote
              name Two
              begin raw_codes
                name A
                  300 9300
              end raw_codes
            end remote
            """, [("test.conf:6", "'end raw_codes' and 'end remote' are missing before")])
        self.assertEqual([remote.name for remote in remotes], ["One", "Two"])

    def test_writer_output_is_read_back(self):
        remote = Remote("Garden", repeat=15)
        remote.codes["Light_on"] = RemoteCode("Light_on", Code(tuple(ON)))
        remote.codes["Light_off"] = RemoteCode("Light_off", Code(tuple(OFF)), 30)
        remotes, problems = parse_text(format_remote(remote), "x.conf", 100)
        self.assertEqual(problems, [])
        self.assertEqual(remotes[0].repeat, 15)
        self.assertEqual({name: (entry.code, entry.repeat) for name, entry in remotes[0].codes.items()},
                         {name: (entry.code, entry.repeat) for name, entry in remote.codes.items()})

    def test_format_code(self):
        self.assertEqual(format_code("New", Code((300, 9300)), 5),
                         ["    name New", "      repeat 5", "      300 9300"])


class LibraryTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.directory)

    def write(self, name, text):
        with open(os.path.join(self.directory, name), "w", encoding="utf-8") as file:
            file.write(text)

    def test_loads_all_conf_files(self):
        self.write("b.conf", support.remote_text("Garden", [support.code_text("On", ON)]))
        self.write("a.conf", "﻿" + support.remote_text("Hall", [support.code_text("Off", OFF)]))
        self.write("notes.txt", "not a code file")
        library = CodeLibrary.load(self.directory, 100)
        self.assertEqual(library.problems, [])
        self.assertEqual(list(library.remotes), ["Hall", "Garden"])
        remote, code = library.find("Garden", "On")
        self.assertEqual(code.code.values, tuple(ON))

    def test_duplicate_remote_in_other_file(self):
        self.write("a.conf", support.remote_text("Garden", [support.code_text("On", ON)]))
        self.write("b.conf", support.remote_text("Garden", [support.code_text("Off", OFF)]))
        library = CodeLibrary.load(self.directory, 100)
        self.assertEqual([str(problem) for problem in library.problems],
                         ["b.conf:1: remote Garden is already defined in a.conf:1"])
        self.assertEqual(list(library.remotes["Garden"].codes), ["On"])

    def test_empty_folder(self):
        library = CodeLibrary.load(self.directory, 100)
        self.assertIn("no code files", str(library.problems[0]))

    def test_find_names_known_entries(self):
        self.write("a.conf", support.remote_text("Garden", [support.code_text("On", ON)]))
        library = CodeLibrary.load(self.directory, 100)
        with self.assertRaisesRegex(Rf433Error, r"unknown remote Hall \(known: Garden\)"):
            library.find("Hall", "On")
        with self.assertRaisesRegex(Rf433Error, r"unknown code Garden Off \(known: On\)"):
            library.find("Garden", "Off")


if __name__ == "__main__":
    unittest.main()
