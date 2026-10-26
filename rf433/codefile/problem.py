from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Problem:
    """A problem in the code files, shown as "file:line: message"."""

    where: str
    message: str

    @classmethod
    def at(cls, path: str, line: int, message: str) -> Problem:
        name = os.path.basename(path)
        return cls("%s:%d" % (name, line) if line else name, message)

    def __str__(self) -> str:
        return "%s: %s" % (self.where, self.message)
