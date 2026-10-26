"""Made-up signals for the tests; no recordings of real remotes."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SHORT = 300
LONG = 900
GAP = 9300


def frame(bits: str, short: int = SHORT, long: int = LONG, gap: int = GAP) -> list[int]:
    """A frame of a typical fixed code socket: 0 = short pulse and long pause, 1 = the other way round."""
    values = []
    for bit in bits:
        values += [long, short] if bit == "1" else [short, long]
    return values + [short, gap]


def jitter(values: list[int], deviations: tuple[int, ...] = (12, -8, 5, -15)) -> list[int]:
    """Deterministic deviations like a receiver adds them: every 7th value differs a little, so the exact
    values stay the most frequent ones, as in a good recording; the gap at the end stays."""
    result = list(values)
    for count, index in enumerate(range(3, len(values) - 1, 7)):
        result[index] += deviations[count % len(deviations)]
    return result


def code_text(name: str, values: list[int], repeat: int | None = None) -> str:
    lines = ["    name %s" % name]
    if repeat is not None:
        lines.append("      repeat %d" % repeat)
    lines.append("      " + " ".join(str(value) for value in values))
    return "\n".join(lines)


def remote_text(name: str, codes: list[str], repeat: int | None = None) -> str:
    lines = ["begin remote", "  name %s" % name]
    if repeat is not None:
        lines.append("  repeat %d" % repeat)
    lines += ["", "  begin raw_codes"] + codes + ["  end raw_codes", "end remote", ""]
    return "\n".join(lines)
