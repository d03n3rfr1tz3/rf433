from __future__ import annotations

from typing import Callable

from .codefile import CodeLibrary
from .options import Options
from .receive.recorder import Recorder
from .transmit.transmitter import Transmitter


def load_library(options: Options) -> CodeLibrary:
    return CodeLibrary.load(options.codes, options.max_repeat)


class Context:
    """What a command works with; tests replace the factories by fakes."""

    def __init__(self, options: Options,
                 transmitter_factory: Callable[[Options], Transmitter],
                 recorder_factory: Callable[[Options], Recorder],
                 library_loader: Callable[[Options], CodeLibrary] = load_library):
        self.options = options
        self.transmitter_factory = transmitter_factory
        self.recorder_factory = recorder_factory
        self.library_loader = library_loader
        self._library: CodeLibrary | None = None

    @property
    def library(self) -> CodeLibrary:
        """The code files, read on first use."""
        if self._library is None:
            self._library = self.library_loader(self.options)
        return self._library

    def transmitter(self) -> Transmitter:
        return self.transmitter_factory(self.options)

    def recorder(self) -> Recorder:
        return self.recorder_factory(self.options)
