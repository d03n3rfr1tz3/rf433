from __future__ import annotations


class Recorder:
    """Records signals for a while; returns packages of values in µs, pulse first."""

    # True if the recorder knows the real pause after the last frame of a package
    last_pause_reliable = False

    def record(self, seconds: int) -> list[list[int]]:
        raise NotImplementedError
