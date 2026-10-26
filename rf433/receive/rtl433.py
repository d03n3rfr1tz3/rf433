"""Recording with rtl_433 and an RTL-SDR stick."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from typing import Callable

from ..errors import Rf433Error
from ..options import LearnOptions
from .ook import parse_ook
from .recorder import Recorder


class Rtl433Recorder(Recorder):
    def __init__(self, options: LearnOptions, log: Callable[[str], None] = print):
        self.options = options
        self.log = log

    def command(self, path: str, seconds: int) -> list[str]:
        options = self.options
        command = ["rtl_433"]
        if options.device:
            command += ["-d", options.device]
        return command + ["-f", options.frequency, "-s", options.sample_rate, "-R", "0", "-A", "-w", path,
                          "-T", str(seconds)]

    def record(self, seconds: int) -> list[list[int]]:
        service = self.options.service
        directory = tempfile.mkdtemp(prefix="rf433-")
        try:
            path = os.path.join(directory, "learn.ook")
            if service:
                self.log("Stopping " + service)
                subprocess.call(["systemctl", "stop", service])
            try:
                self.log("Recording for %d seconds, press the button now" % seconds)
                subprocess.call(self.command(path, seconds))
            except FileNotFoundError:
                raise Rf433Error("rtl_433 not found, please install it")
            finally:
                if service:
                    self.log("Starting " + service)
                    subprocess.call(["systemctl", "start", service])

            if not os.path.exists(path):
                raise Rf433Error("rtl_433 wrote no recording")
            with open(path, "r") as file:
                return parse_ook(file.read())
        finally:
            shutil.rmtree(directory, ignore_errors=True)
