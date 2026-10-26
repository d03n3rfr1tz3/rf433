"""Sending through a LIRC device of gpio-ir-tx with carrier 0."""

from __future__ import annotations

import array
import os
import struct
import time
from typing import Callable

from ..errors import Rf433Error
from ..model import Code
from . import realtime
from .transmitter import SendReport, Transmitter
from .windows import plan_windows

LIRC_SET_SEND_CARRIER = 0x40046913      # _IOW('i', 0x00000013, __u32)


class LircTransmitter(Transmitter):
    def __init__(self, device: str, cpu_core: int | None = None, priority: int = 50,
                 warn: Callable[[str], None] = print):
        self.device = device
        self.cpu_core = cpu_core
        self.priority = priority
        self.warn = warn

    def send(self, code: Code, repeat: int) -> SendReport:
        try:
            import fcntl
        except ImportError:
            raise Rf433Error("sending needs Linux with a LIRC device")

        code.check()
        windows = plan_windows(code, repeat)
        values = list(code.values)
        buffers = {count: array.array("I", (values * count)[:-1]) for count in set(windows)}

        for warning in realtime.prioritize(self.cpu_core, self.priority):
            self.warn(warning)
        fd = os.open(self.device, os.O_WRONLY)
        try:
            # one sender at a time, windows of two commands must not interleave
            fcntl.flock(fd, fcntl.LOCK_EX)
            fcntl.ioctl(fd, LIRC_SET_SEND_CARRIER, struct.pack("I", 0))

            lateness = 0
            target = None
            for count in windows:
                if target is not None:
                    realtime.wait_until(target)
                    lateness = max(lateness, time.perf_counter_ns() - target)
                data = buffers[count]
                written = os.write(fd, data)
                if written != len(data) * data.itemsize:
                    raise Rf433Error("short write: %d of %d bytes" % (written, len(data) * data.itemsize))
                # write returns after the signal is out, the pause starts now
                target = time.perf_counter_ns() + code.pause * 1000
        finally:
            os.close(fd)
        return SendReport(windows, lateness)
