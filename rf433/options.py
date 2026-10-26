"""Settings of rf433: defaults, overridden by the options file, overridden by the command line."""

from __future__ import annotations

import configparser
import os
from dataclasses import dataclass, field

from .errors import Rf433Error

DEFAULT_OPTIONS_FILE = "/etc/rf433/rf433_options.conf"


@dataclass
class LearnOptions:
    device: str = ""                    # rtl_433 device (-d), empty = rtl_433 default
    frequency: str = "433.92M"          # rtl_433 frequency (-f)
    sample_rate: str = "250k"           # rtl_433 sample rate (-s)
    seconds: int = 10                   # recording time
    service: str = ""                   # systemd service using the stick, stopped while learning


@dataclass
class Options:
    device: str = "/dev/lirc0"          # LIRC device of the 433 MHz sender
    codes: str = "/etc/rf433/rf433.conf.d"
    repeat: int = 10                    # frames sent when neither code nor remote sets repeat
    max_repeat: int = 100               # upper limit, protects against typos
    cpu_core: int | None = None         # CPU core used while sending, None = the highest one
    priority: int = 50                  # SCHED_FIFO priority while sending
    learn: LearnOptions = field(default_factory=LearnOptions)

    @classmethod
    def load(cls, path: str | None = None, device: str | None = None, codes: str | None = None) -> Options:
        """Reads the options file (the default file may be missing) and applies the command line."""
        options = cls()
        if path is None:
            if os.path.exists(DEFAULT_OPTIONS_FILE):
                options.read(DEFAULT_OPTIONS_FILE)
        else:
            options.read(path)
        if device is not None:
            options.device = device
        if codes is not None:
            options.codes = codes
        return options

    def read(self, path: str) -> None:
        parser = configparser.ConfigParser(interpolation=None)
        try:
            with open(path, "r", encoding="utf-8") as file:
                parser.read_file(file)
        except configparser.Error as error:
            raise Rf433Error("%s: %s" % (path, error))

        for section in parser.sections():
            if section not in ("rf433", "learn"):
                raise Rf433Error("%s: unknown section [%s]" % (path, section))
        reader = _SectionReader(path, parser, "rf433")
        self.device = reader.text("device", self.device)
        self.codes = reader.text("codes", self.codes)
        self.max_repeat = reader.number("max_repeat", self.max_repeat, 1)
        self.repeat = reader.number("repeat", self.repeat, 1, self.max_repeat)
        self.cpu_core = reader.number("cpu_core", self.cpu_core, 0)
        self.priority = reader.number("priority", self.priority, 1, 99)
        reader.check_unknown()

        reader = _SectionReader(path, parser, "learn")
        self.learn.device = reader.text("device", self.learn.device)
        self.learn.frequency = reader.text("frequency", self.learn.frequency)
        self.learn.sample_rate = reader.text("sample_rate", self.learn.sample_rate)
        self.learn.seconds = reader.number("seconds", self.learn.seconds, 1)
        self.learn.service = reader.text("service", self.learn.service)
        reader.check_unknown()


class _SectionReader:
    def __init__(self, path: str, parser: configparser.ConfigParser, section: str):
        self.path = path
        self.section = section
        self.values = dict(parser.items(section)) if parser.has_section(section) else {}
        self.used: set[str] = set()

    def text(self, key: str, default: str) -> str:
        self.used.add(key)
        return self.values.get(key, default)

    def number(self, key: str, default, minimum: int, maximum: int | None = None):
        """An integer in the given range; an empty value means the default (None for cpu_core)."""
        self.used.add(key)
        text = self.values.get(key, "")
        if text == "":
            return default
        try:
            value = int(text)
        except ValueError:
            value = None
        if value is None or value < minimum or (maximum is not None and value > maximum):
            limit = "from %d" % minimum if maximum is None else "from %d to %d" % (minimum, maximum)
            raise Rf433Error("%s: [%s] %s must be a number %s, got %r" % (self.path, self.section, key, limit, text))
        return value

    def check_unknown(self) -> None:
        unknown = sorted(set(self.values) - self.used)
        if unknown:
            raise Rf433Error("%s: [%s] unknown option %s" % (self.path, self.section, ", ".join(unknown)))
