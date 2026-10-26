from __future__ import annotations

import os
from dataclasses import dataclass, field

from .code import Code


@dataclass
class RemoteCode:
    name: str
    code: Code
    repeat: int | None = None           # own setting, None = the one of the remote
    line: int = 0


@dataclass
class Remote:
    name: str
    path: str = ""
    line: int = 0
    repeat: int | None = None           # own setting, None = the default of the options
    codes: dict[str, RemoteCode] = field(default_factory=dict)

    @property
    def file(self) -> str:
        return os.path.basename(self.path)

    def repeat_of(self, code: RemoteCode | None, default: int) -> int:
        """Repeat of a code, or of the remote itself for None."""
        if code is not None and code.repeat is not None:
            return code.repeat
        if self.repeat is not None:
            return self.repeat
        return default
