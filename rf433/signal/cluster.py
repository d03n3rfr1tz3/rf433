"""Merging of values that differ only by jitter."""

from __future__ import annotations

import collections

DEFAULT_TOLERANCE = 0.25                # relative distance of values that are merged


def cluster_values(values: list[int], tolerance: float) -> dict[int, int]:
    """Sorted values form one group while each is at most (1 + tolerance) times the previous one;
    every value maps to the most frequent value of its group."""
    counts = collections.Counter(values)
    mapping = {}
    group = []
    for value in sorted(counts) + [None]:
        if group and (value is None or value > group[-1] * (1 + tolerance)):
            best = max(group, key=lambda item: counts[item])
            for item in group:
                mapping[item] = best
            group = []
        if value is not None:
            group.append(value)
    return mapping


def clean_codes(codes: list[list[int]], tolerance: float) -> list[list[int]]:
    """Pulses and pauses are grouped separately, over all given codes together."""
    pulses = cluster_values([value for values in codes for value in values[0::2]], tolerance)
    pauses = cluster_values([value for values in codes for value in values[1::2]], tolerance)
    return [[pulses[value] if index % 2 == 0 else pauses[value] for index, value in enumerate(values)]
            for values in codes]


def clean_code(values: list[int], tolerance: float) -> list[int]:
    return clean_codes([values], tolerance)[0]
