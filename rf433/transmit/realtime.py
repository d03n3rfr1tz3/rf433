"""CPU core, scheduler and precise waiting while sending (Linux only)."""

from __future__ import annotations


def prioritize(cpu_core: int | None, priority: int) -> list[str]:
    raise NotImplementedError


def wait_until(target_ns: int) -> None:
    raise NotImplementedError
