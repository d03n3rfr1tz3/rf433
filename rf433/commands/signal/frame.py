from ...model import Code
from ...signal.frames import DEFAULT_MIN_GAP, extract_frame
from ..base import Command


class FrameCommand(Command):
    name = "frame"
    help = "cut one frame including its pause out of a recording with repeats"

    def add_arguments(self, parser):
        parser.add_argument("--code", "-c", required=True)
        parser.add_argument("--min-gap", type=int, default=DEFAULT_MIN_GAP,
                            help="pauses of at least this many µs end a frame (default %(default)s)")

    def run(self, args, context):
        values = list(Code.parse(args.code).values)
        result = extract_frame([values], args.min_gap, True)
        print(" --> %d frames, %d of them with %d values" % (result.frames, result.matches, len(result.values)))
        print(Code(tuple(result.values)).format())
        return 0
