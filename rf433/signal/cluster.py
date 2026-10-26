"""Merging of values that differ only by jitter."""

from __future__ import annotations

DEFAULT_TOLERANCE = 0.25                # relative distance of values that are merged


def cluster_values(values: list[int], tolerance: float) -> dict[int, int]:
    raise NotImplementedError


def clean_codes(codes: list[list[int]], tolerance: float) -> list[list[int]]:
    raise NotImplementedError


def clean_code(values: list[int], tolerance: float) -> list[int]:
    return clean_codes([values], tolerance)[0]
