"""Cutting one frame out of a recording with repeats."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_MIN_GAP = 5000                  # in µs; pauses of at least this length end a frame


@dataclass
class ExtractedFrame:
    values: list[int]
    frames: int                         # frames found in total
    matches: int                        # frames with the length of the result


def split_frames(values: list[int], min_gap: int) -> list[tuple[list[int], bool]]:
    raise NotImplementedError


def extract_frame(packages: list[list[int]], min_gap: int, last_pause_reliable: bool) -> ExtractedFrame:
    raise NotImplementedError
