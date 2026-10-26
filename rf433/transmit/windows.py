"""Packing of the repeats into writes ("windows") within the kernel limits."""

from __future__ import annotations

from ..errors import Rf433Error
from ..model import Code
from .limits import IR_MAX_DURATION, LIRCBUF_SIZE


def frames_per_window(code: Code) -> int:
    """Frames of one write: the last pause of a window is left out, the sender keeps it by waiting."""
    return min((IR_MAX_DURATION + code.pause) // code.duration, (LIRCBUF_SIZE + 1) // len(code.values))


def plan_windows(code: Code, repeat: int) -> list[int]:
    """Frames per write, as many as possible in each."""
    per_window = frames_per_window(code)
    if per_window < 1:
        raise Rf433Error("; ".join(code.problems()) or "code does not fit into one write")
    windows = []
    while repeat > 0:
        count = min(per_window, repeat)
        windows.append(count)
        repeat -= count
    return windows


def describe(code: Code, repeat: int) -> str:
    windows = plan_windows(code, repeat)
    return "%.1f ms x %d = %d window%s (%s)" % (code.duration / 1000, repeat, len(windows),
                                                "" if len(windows) == 1 else "s", "+".join(str(count) for count in windows))
