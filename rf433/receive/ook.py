"""Pulse data of rtl_433 (-w file.ook)."""

from __future__ import annotations


def parse_ook(text: str) -> list[list[int]]:
    """";ook N pulses" or ";fsk N pulses", then lines "pulse gap" in µs, ";end"; one package each."""
    packages = []
    current = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(";ook") or line.startswith(";fsk"):
            current = []
            packages.append(current)
        elif line.startswith(";end"):
            current = None
        elif line and not line.startswith(";") and current is not None:
            parts = line.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                current.extend([int(parts[0]), int(parts[1])])
    return [package for package in packages if package]
