"""Recording with rtl_433 and an RTL-SDR stick."""

from __future__ import annotations

from typing import Callable

from ..options import LearnOptions
from .recorder import Recorder


class Rtl433Recorder(Recorder):
    def __init__(self, options: LearnOptions, log: Callable[[str], None] = print):
        self.options = options
        self.log = log

    def record(self, seconds: int) -> list[list[int]]:
        raise NotImplementedError
