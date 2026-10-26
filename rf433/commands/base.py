from __future__ import annotations

import argparse

from ..context import Context
from ..errors import Rf433Error
from ..model import Remote, RemoteCode


class Command:
    """One subcommand of the command line."""

    name = ""
    help = ""

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        pass

    def run(self, args: argparse.Namespace, context: Context) -> int:
        raise NotImplementedError


def find_code(context: Context, remote_name: str, code_name: str) -> tuple[Remote, RemoteCode]:
    """A code of the code files; the problems of the files are shown when it is missing."""
    library = context.library
    try:
        return library.find(remote_name, code_name)
    except Rf433Error:
        for problem in library.problems:
            print(" --> Warning: %s" % problem)
        raise
