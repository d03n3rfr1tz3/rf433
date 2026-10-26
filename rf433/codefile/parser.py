"""Reads code files: "begin remote" blocks with raw_codes, similar to lircd.conf (see docs/code-files.md)."""

from __future__ import annotations

from ..model import Remote
from .problem import Problem


def parse_text(text: str, path: str, max_repeat: int) -> tuple[list[Remote], list[Problem]]:
    raise NotImplementedError


def parse_file(path: str, max_repeat: int) -> tuple[list[Remote], list[Problem]]:
    with open(path, "r", encoding="utf-8-sig") as file:
        return parse_text(file.read(), path, max_repeat)
