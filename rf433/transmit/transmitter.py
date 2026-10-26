from __future__ import annotations

from dataclasses import dataclass

from ..model import Code


@dataclass
class SendReport:
    windows: list[int]                  # frames per write
    lateness_ns: int = 0                # longest delay of a pause between two writes


class Transmitter:
    """Sends one code a given number of times."""

    def send(self, code: Code, repeat: int) -> SendReport:
        raise NotImplementedError
