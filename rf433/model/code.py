from __future__ import annotations

import re
from dataclasses import dataclass

from ..errors import Rf433Error
from ..transmit.limits import IR_MAX_DURATION, LIRCBUF_SIZE


@dataclass(frozen=True)
class Code:
    """One frame of a signal including the pause after it: durations in µs, pulse first."""

    values: tuple[int, ...]

    @classmethod
    def parse(cls, text: str) -> Code:
        # accepts "270 2700 ...", "270,2700,..." and "+270 -2700 ..."; signs are ignored, the order counts
        values = []
        for part in re.split(r"[\s,]+", text.strip()):
            if part == "":
                continue
            number = part.lstrip("+-")
            if not number.isdigit():
                raise Rf433Error("invalid value in code: " + part)
            values.append(int(number))
        return cls(tuple(values))

    def format(self) -> str:
        return " ".join(str(value) for value in self.values)

    @property
    def duration(self) -> int:
        """Duration of one frame including its pause, in µs."""
        return sum(self.values)

    @property
    def pause(self) -> int:
        return self.values[-1]

    def problems(self) -> list[str]:
        values = self.values
        if len(values) < 2:
            return ["code needs at least one pulse and one pause"]
        problems = []
        if len(values) % 2 != 0:
            problems.append("code must end with a pause (even number of values, got %d)" % len(values))
        if 0 in values:
            problems.append("code contains zero values")
        if len(values) - 1 > LIRCBUF_SIZE:
            problems.append("code has %d values, at most %d fit into one write" % (len(values), LIRCBUF_SIZE + 1))
        if sum(values[:-1]) > IR_MAX_DURATION:
            problems.append("code is %.1f ms long, at most %d ms fit into one write"
                            % (sum(values[:-1]) / 1000, IR_MAX_DURATION // 1000))
        return problems

    def check(self) -> Code:
        problems = self.problems()
        if problems:
            raise Rf433Error("; ".join(problems))
        return self


def check_repeat(repeat, max_repeat: int) -> int:
    if isinstance(repeat, bool) or not isinstance(repeat, int) or repeat < 1 or repeat > max_repeat:
        raise Rf433Error("repeat must be a number from 1 to %d, got %r" % (max_repeat, repeat))
    return repeat
