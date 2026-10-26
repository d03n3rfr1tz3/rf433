"""CPU core, scheduler and precise waiting while sending (Linux only)."""

from __future__ import annotations

import os
import time

SPIN_MARGIN = 2000000                   # in ns; busy waiting starts this long before the target


def prioritize(cpu_core: int | None, priority: int) -> list[str]:
    """Binds the process to one CPU core and switches to SCHED_FIFO; returns warnings for what failed."""
    warnings = []
    # gpio-ir-tx blocks the interrupts of its CPU core while sending; keep USB and network on the other cores
    try:
        cores = os.sched_getaffinity(0)
        core = cpu_core if cpu_core in cores else max(cores)
        os.sched_setaffinity(0, {core})
    except (AttributeError, OSError) as error:
        warnings.append("could not bind to a CPU core: %s" % error)

    # precise pauses between the windows
    try:
        os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(priority))
    except (AttributeError, OSError) as error:
        warnings.append("could not set SCHED_FIFO: %s" % error)
    return warnings


def wait_until(target_ns: int) -> None:
    """Sleeps most of the time (no RT throttling) and busy waits the rest (precision)."""
    remaining = target_ns - time.perf_counter_ns() - SPIN_MARGIN
    if remaining > 0:
        time.sleep(remaining / 1000000000)
    while time.perf_counter_ns() < target_ns:
        pass
