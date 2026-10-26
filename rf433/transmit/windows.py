"""Packing of the repeats into writes ("windows") within the kernel limits."""

from __future__ import annotations

from ..model import Code


def frames_per_window(code: Code) -> int:
    raise NotImplementedError


def plan_windows(code: Code, repeat: int) -> list[int]:
    raise NotImplementedError


def describe(code: Code, repeat: int) -> str:
    raise NotImplementedError
