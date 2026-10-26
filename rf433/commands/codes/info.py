from ...errors import Rf433Error
from ...model import Code, check_repeat
from ...transmit.windows import describe, frames_per_window
from ..base import Command, find_code


class InfoCommand(Command):
    name = "info"
    help = "show duration and windows of a code without sending"

    def add_arguments(self, parser):
        parser.add_argument("remote", nargs="?")
        parser.add_argument("name", nargs="?", metavar="code")
        parser.add_argument("--code", "-c", dest="values", help="values in µs instead of remote and code")
        parser.add_argument("--repeat", "-r", type=int)

    def run(self, args, context):
        if args.values is not None:
            if args.remote is not None:
                raise Rf433Error("either --code or remote and code")
            code, repeat, label = Code.parse(args.values), context.options.repeat, "code"
        elif args.remote is not None and args.name is not None:
            remote, entry = find_code(context, args.remote, args.name)
            code, repeat = entry.code, remote.repeat_of(entry, context.options.repeat)
            label = "%s %s" % (remote.name, entry.name)
        else:
            raise Rf433Error("remote and code or --code are required")

        code.check()
        repeat = check_repeat(repeat if args.repeat is None else args.repeat, context.options.max_repeat)
        print("%s: %d values, pulse first, pause at the end %d µs" % (label, len(code.values), code.pause))
        print("Duration %.1f ms, at most %d per window" % (code.duration / 1000, frames_per_window(code)))
        print(describe(code, repeat))
        return 0
