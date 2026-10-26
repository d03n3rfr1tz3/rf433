from ...model import Code
from ..base import Command
from . import transmit


class RawCommand(Command):
    name = "raw"
    help = "send a code given on the command line"

    def add_arguments(self, parser):
        parser.add_argument("--code", "-c", required=True, help="values in µs, pulse first, ending with a pause")
        parser.add_argument("--repeat", "-r", type=int, help="default: repeat of the options")

    def run(self, args, context):
        repeat = args.repeat if args.repeat is not None else context.options.repeat
        transmit(context, Code.parse(args.code), repeat, "raw code")
        return 0
