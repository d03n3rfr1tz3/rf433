import collections

from ...model import Code
from ...signal.cluster import DEFAULT_TOLERANCE, clean_code
from ..base import Command


class CleanCommand(Command):
    name = "clean"
    help = "suggest a cleaned code: pulses and pauses within the tolerance get the same value"

    def add_arguments(self, parser):
        parser.add_argument("--code", "-c", required=True)
        parser.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE,
                            help="relative distance of merged values (default %(default)s)")

    def run(self, args, context):
        values = list(Code.parse(args.code).values)
        cleaned = clean_code(values, args.tolerance)
        changes = collections.Counter((value, new) for value, new in zip(values, cleaned) if value != new)
        for (value, new), count in sorted(changes.items()):
            print(" --> %d -> %d (%dx)" % (value, new, count))
        if not changes:
            print(" --> nothing to clean")
        print(Code(tuple(cleaned)).format())
        return 0
