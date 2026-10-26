"""Cutting one frame out of a recording with repeats."""

from __future__ import annotations

import collections
from dataclasses import dataclass

from ..errors import Rf433Error

DEFAULT_MIN_GAP = 5000                  # in µs; pauses of at least this length end a frame


@dataclass
class ExtractedFrame:
    values: list[int]
    frames: int                         # frames found in total
    matches: int                        # frames with the length of the result


def split_frames(values: list[int], min_gap: int) -> list[tuple[list[int], bool]]:
    """[(frame, ends with a gap)]; a frame ends with a pause of at least min_gap."""
    frames = []
    frame: list[int] = []
    for index in range(0, len(values) - 1, 2):
        frame.extend(values[index:index + 2])
        if values[index + 1] >= min_gap:
            frames.append((frame, True))
            frame = []
    if frame:
        frames.append((frame, False))
    return frames


def extract_frame(packages: list[list[int]], min_gap: int, last_pause_reliable: bool) -> ExtractedFrame:
    """The middle frame of the most frequent length; its pause is the median of the reliable pauses.
    The last pause of a package is only trusted if last_pause_reliable."""
    frames = []
    for values in packages:
        parts = split_frames(values, min_gap)
        for index, (frame, ends_with_gap) in enumerate(parts):
            reliable = ends_with_gap and (last_pause_reliable or index < len(parts) - 1)
            frames.append((frame, reliable))
    if not frames:
        raise Rf433Error("no frames found")

    lengths = collections.Counter(len(frame) for frame, reliable in frames)
    length = max(lengths, key=lambda item: (lengths[item], item))
    candidates = [(frame, reliable) for frame, reliable in frames if len(frame) == length]
    pauses = sorted(frame[-1] for frame, reliable in candidates if reliable)

    result = list(candidates[len(candidates) // 2][0])
    if pauses:
        result[-1] = pauses[len(pauses) // 2]
    return ExtractedFrame(result, len(frames), len(candidates))
