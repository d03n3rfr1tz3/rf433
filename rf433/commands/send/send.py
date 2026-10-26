from ..base import Command, find_code
from . import transmit


class SendCommand(Command):
    name = "send"
    help = "send a code of the code files"

    def add_arguments(self, parser):
        parser.add_argument("remote")
        parser.add_argument("name", metavar="code")
        parser.add_argument("--repeat", "-r", type=int, help="overrides the repeat of the code file")

    def run(self, args, context):
        remote, entry = find_code(context, args.remote, args.name)
        repeat = args.repeat if args.repeat is not None else remote.repeat_of(entry, context.options.repeat)
        transmit(context, entry.code, repeat, "%s %s" % (remote.name, entry.name))
        return 0
