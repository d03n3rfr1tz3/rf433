from ...codefile import format_code
from ...errors import Rf433Error
from ...model import Code
from ...signal.cluster import DEFAULT_TOLERANCE, clean_code
from ...signal.frames import DEFAULT_MIN_GAP, extract_frame
from ...transmit.windows import describe
from ..base import Command


class LearnCommand(Command):
    name = "learn"
    help = "record a remote and print a code for the code file"

    def add_arguments(self, parser):
        parser.add_argument("--seconds", type=int, help="recording time (default: seconds of the options)")
        parser.add_argument("--name", default="New", help="code name of the printed code (default %(default)s)")
        parser.add_argument("--min-gap", type=int, default=DEFAULT_MIN_GAP,
                            help="pauses of at least this many µs end a frame (default %(default)s)")
        parser.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE,
                            help="relative distance of merged values (default %(default)s)")

    def run(self, args, context):
        recorder = context.recorder()
        packages = recorder.record(args.seconds if args.seconds is not None else context.options.learn.seconds)
        if not packages:
            raise Rf433Error("nothing received")

        result = extract_frame(packages, args.min_gap, recorder.last_pause_reliable)
        code = Code(tuple(clean_code(result.values, args.tolerance)))
        print(" --> %d packages, %d frames, %d of them with %d values"
              % (len(packages), result.frames, result.matches, len(result.values)))
        print(" --> Recorded: %s" % Code(tuple(result.values)).format())
        code.check()
        print(" --> %s" % describe(code, context.options.repeat))
        print("")
        print("\n".join(format_code(args.name, code)))
        return 0
