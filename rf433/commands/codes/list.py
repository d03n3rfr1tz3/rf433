import json

from ...transmit.windows import describe
from ..base import Command


class ListCommand(Command):
    name = "list"
    help = "list remotes and codes"

    def add_arguments(self, parser):
        parser.add_argument("remote", nargs="?", help="only this remote")
        parser.add_argument("--json", action="store_true", help="remotes, codes and problems as JSON")

    def run(self, args, context):
        library = context.library
        default = context.options.repeat
        remotes = [remote for remote in library.remotes.values() if args.remote is None or remote.name == args.remote]

        if args.json:
            result = {"remotes": [], "problems": [str(problem) for problem in library.problems]}
            for remote in remotes:
                codes = [{"name": entry.name, "repeat": remote.repeat_of(entry, default), "values": list(entry.code.values),
                          "duration_us": entry.code.duration} for entry in remote.codes.values()]
                result["remotes"].append({"name": remote.name, "file": remote.file,
                                          "repeat": remote.repeat_of(None, default), "codes": codes})
            print(json.dumps(result, indent=1, ensure_ascii=False))
            return 1 if library.problems else 0

        for remote in remotes:
            print("%s (%s)" % (remote.name, remote.file))
            for entry in remote.codes.values():
                print("  %-20s %s" % (entry.name, describe(entry.code, remote.repeat_of(entry, default))))
        for problem in library.problems:
            print("Problem: %s" % problem)
        return 1 if library.problems else 0
