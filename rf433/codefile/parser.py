"""Reads code files: "begin remote" blocks with raw_codes, similar to lircd.conf (see docs/code-files.md)."""

from __future__ import annotations

import re

from ..errors import Rf433Error
from ..model import Code, Remote, RemoteCode, check_repeat
from .problem import Problem

NAME = re.compile(r"[A-Za-z0-9_-]+$")


class _Parser:
    def __init__(self, path: str, max_repeat: int):
        self.path = path
        self.max_repeat = max_repeat
        self.remotes: list[Remote] = []
        self.problems: list[Problem] = []
        self.remote: Remote | None = None       # inside "begin remote"
        self.in_codes = False                   # inside "begin raw_codes"
        self.code: RemoteCode | None = None     # the code being read, values follow
        self.code_valid = True
        self.values: list[str] = []
        self.values_line = 0

    def problem(self, line: int, message: str) -> None:
        self.problems.append(Problem.at(self.path, line, message))

    def parse(self, text: str) -> None:
        number = 0
        for number, line in enumerate(text.splitlines(), 1):
            words = line.split()
            if not words or words[0].startswith("#"):
                continue
            if self.in_codes:
                self.code_line(number, words)
            elif self.remote is not None:
                self.remote_line(number, words)
            elif words == ["begin", "remote"]:
                self.remote = Remote("", self.path, number)
            else:
                self.problem(number, "expected 'begin remote', got '%s'" % " ".join(words))
        if self.in_codes:
            self.problem(number, "'end raw_codes' is missing")
            self.end_codes()
        if self.remote is not None:
            self.problem(number, "'end remote' is missing")
            self.end_remote()

    def remote_line(self, number: int, words: list[str]) -> None:
        remote = self.remote
        key = words[0]
        if key == "name":
            name = self.name(number, words)
            if remote.name and name:
                self.problem(number, "remote %s has a second name %s" % (remote.name, name))
            elif name:
                remote.name = name
        elif key == "repeat":
            remote.repeat = self.repeat(number, words)
        elif words == ["begin", "raw_codes"]:
            self.in_codes = True
        elif words == ["end", "remote"]:
            self.end_remote()
        elif words == ["begin", "remote"]:
            self.problem(number, "'end remote' is missing before")
            self.end_remote()
            self.remote = Remote("", self.path, number)
        else:
            self.problem(number, "unknown keyword '%s' in remote" % key)

    def code_line(self, number: int, words: list[str]) -> None:
        key = words[0]
        if key[0].isdigit() or key[0] in "+-":
            if self.code is None:
                self.problem(number, "values without 'name' before")
                return
            if not self.values:
                self.values_line = number
            self.values += words
        elif key == "name":
            self.end_code()
            name = self.name(number, words)
            self.code = RemoteCode(name or "", Code(()), None, number)
            self.code_valid = name is not None
        elif key == "repeat":
            if self.code is None or self.values:
                self.problem(number, "'repeat' belongs directly below the name of a code")
                return
            repeat = self.repeat(number, words)
            if repeat is None:
                self.code_valid = False
            self.code.repeat = repeat
        elif words == ["end", "raw_codes"]:
            self.end_codes()
        elif words == ["end", "remote"]:
            self.problem(number, "'end raw_codes' is missing before")
            self.end_codes()
            self.end_remote()
        elif words == ["begin", "remote"]:
            self.problem(number, "'end raw_codes' and 'end remote' are missing before")
            self.end_codes()
            self.end_remote()
            self.remote = Remote("", self.path, number)
        else:
            self.problem(number, "unknown keyword '%s' in raw_codes" % key)

    def name(self, number: int, words: list[str]) -> str | None:
        if len(words) != 2 or not NAME.match(words[1]):
            self.problem(number, "name must be one word of letters, digits, _ and -, got '%s'" % " ".join(words[1:]))
            return None
        return words[1]

    def repeat(self, number: int, words: list[str]) -> int | None:
        try:
            if len(words) != 2 or not words[1].isdigit():
                raise Rf433Error("repeat must be a number from 1 to %d, got '%s'" % (self.max_repeat, " ".join(words[1:])))
            return check_repeat(int(words[1]), self.max_repeat)
        except Rf433Error as error:
            self.problem(number, str(error))
            return None

    def end_code(self) -> None:
        code, values = self.code, self.values
        self.code, self.values = None, []
        if code is None or not self.code_valid:
            return
        where = "%s %s" % (self.remote.name or "remote", code.name)
        if not values:
            self.problem(code.line, "%s: values are missing" % where)
            return
        try:
            code.code = Code.parse(" ".join(values))
        except Rf433Error as error:
            self.problem(self.values_line, "%s: %s" % (where, error))
            return
        problems = code.code.problems()
        if problems:
            self.problem(self.values_line, "%s: %s" % (where, "; ".join(problems)))
            return
        other = self.remote.codes.get(code.name)
        if other is not None:
            self.problem(code.line, "%s is already defined in line %d" % (where, other.line))
            return
        self.remote.codes[code.name] = code

    def end_codes(self) -> None:
        self.end_code()
        self.in_codes = False

    def end_remote(self) -> None:
        remote = self.remote
        self.remote = None
        if not remote.name:
            self.problem(remote.line, "remote without name, its codes are ignored")
        elif not remote.codes:
            self.problem(remote.line, "remote %s has no codes" % remote.name)
        else:
            self.remotes.append(remote)


def parse_text(text: str, path: str, max_repeat: int) -> tuple[list[Remote], list[Problem]]:
    parser = _Parser(path, max_repeat)
    parser.parse(text)
    return parser.remotes, parser.problems


def parse_file(path: str, max_repeat: int) -> tuple[list[Remote], list[Problem]]:
    with open(path, "r", encoding="utf-8-sig") as file:
        return parse_text(file.read(), path, max_repeat)
