from __future__ import annotations

from ...context import Context
from ...model import Code, check_repeat
from ...transmit.windows import describe


def transmit(context: Context, code: Code, repeat: int, label: str) -> None:
    code.check()
    check_repeat(repeat, context.options.max_repeat)
    print(" --> Sending %s: %s" % (label, describe(code, repeat)))
    report = context.transmitter().send(code, repeat)
    print(" --> Done, pauses between windows at most %.3f ms late" % (report.lateness_ns / 1000000))
