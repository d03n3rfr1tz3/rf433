"""Sending through a LIRC device of gpio-ir-tx with carrier 0."""

from __future__ import annotations

from typing import Callable

from ..model import Code
from .transmitter import SendReport, Transmitter


class LircTransmitter(Transmitter):
    def __init__(self, device: str, cpu_core: int | None = None, priority: int = 50,
                 warn: Callable[[str], None] = print):
        self.device = device
        self.cpu_core = cpu_core
        self.priority = priority
        self.warn = warn

    def send(self, code: Code, repeat: int) -> SendReport:
        raise NotImplementedError
