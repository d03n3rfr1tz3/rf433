from __future__ import annotations

import glob
import os

from ..errors import Rf433Error
from ..model import Remote, RemoteCode
from .parser import parse_file
from .problem import Problem


class CodeLibrary:
    """All remotes of the code folder (*.conf), plus the problems found while reading them."""

    def __init__(self, remotes: dict[str, Remote] | None = None, problems: list[Problem] | None = None):
        self.remotes = remotes if remotes is not None else {}
        self.problems = problems if problems is not None else []

    @classmethod
    def load(cls, directory: str, max_repeat: int) -> CodeLibrary:
        library = cls()
        paths = sorted(glob.glob(os.path.join(glob.escape(directory), "*.conf")))
        if not paths:
            library.problems.append(Problem(directory, "no code files (*.conf)"))
        for path in paths:
            try:
                remotes, problems = parse_file(path, max_repeat)
            except (OSError, UnicodeDecodeError) as error:
                library.problems.append(Problem.at(path, 0, str(error)))
                continue
            library.problems += problems
            for remote in remotes:
                library.add(remote)
        return library

    def add(self, remote: Remote) -> None:
        other = self.remotes.get(remote.name)
        if other is not None:
            self.problems.append(Problem.at(remote.path, remote.line, "remote %s is already defined in %s:%d"
                                            % (remote.name, other.file, other.line)))
            return
        self.remotes[remote.name] = remote

    def find(self, remote_name: str, code_name: str) -> tuple[Remote, RemoteCode]:
        remote = self.remotes.get(remote_name)
        if remote is None:
            raise Rf433Error("unknown remote %s (known: %s)" % (remote_name, ", ".join(self.remotes) or "none"))
        code = remote.codes.get(code_name)
        if code is None:
            raise Rf433Error("unknown code %s %s (known: %s)" % (remote_name, code_name, ", ".join(remote.codes) or "none"))
        return remote, code
